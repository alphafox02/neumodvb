/*
 * Neumo dvb (C) 2019-2025 deeptho@gmail.com
 * Copyright notice:
 *
 * This program is free software; you can redistribute it and/or modify
 * it under the terms of the GNU General Public License as published by
 * the Free Software Foundation; either version 2 of the License, or
 * (at your option) any later version.
 *
 * This program is distributed in the hope that it will be useful,
 * but WITHOUT ANY WARRANTY; without even the implied warranty of
 * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
 * GNU General Public License for more details.
 *
 * You should have received a copy of the GNU General Public License
 * along with this program; if not, write to the Free Software
 * Foundation, Inc., 675 Mass Ave, Cambridge, MA 02139, USA.
 *
 */
#include "util/dtassert.h"
#include "epgdb_extra.h"
#include "../chdb/chdb_extra.h"
#include "fmt/chrono.h"
#include "neumodb/db_keys_helper.h"
#include "neumotime.h"

using namespace epgdb;

/*
	remove epg data on all services, earlier than start_time
*/

void epgdb::clean(db_txn& txnepg, system_time_t start_time) {
	dttime_init();
	bool use_log = txnepg.use_log;
	txnepg.use_log = false;
	epgdb::epgdb_t::clean_log(txnepg, 10000);
	auto c = find_first<epg_record_t>(txnepg);
	while (c.is_valid()) {
		auto x = c.current();
		epgdb::epg_record_t end{};
		/*make a key pointing to the first not to be deleted record*/
		end.k = x.k;				// copy of x, only used for its key part
		x.k.start_time = 0; // needed later
		end.k.start_time = system_clock_t::to_time_t(start_time);
		auto sk_end = epg_record_t::make_key(epg_record_t::keys_t::key, epg_record_t::partial_keys_t::service_start_time,
																				 &end, false);
		lmdb::val k{}, v{};
		for (; c.is_valid(); c.next()) {
			const bool found = c.get(k, v, MDB_GET_CURRENT);
#pragma unused(found)
#ifndef NDEBUG
			assert(found);
#endif
			if (memcmp((void*)k.data(), (void*)sk_end.buffer(), sk_end.size()) >= 0)
				break; // we have reached the first record to keep
			delete_record_at_cursor(c);
		}
		if (!c.is_valid())
			break;
		// move to next channel
		auto sk_next = epg_record_t::make_key(epg_record_t::keys_t::key, epg_record_t::partial_keys_t::service, &x, true);
		if (!c.find(sk_next, MDB_SET_RANGE))
			break;
	}
	auto t = dttime(-1);
	txnepg.use_log = use_log;
	dtdebugf("Cleaned epg: {} milliseconds", t);
}

/*compute duration of overlapping part between [a1,a2] and [b1,b2]
	Overlap = 1 if [a1,a2[ is filly contained in [b1,b2[
	otherwise it
	b1 b2 a1 a2  => left =a1 right= b2 => right - left <0 no overlap
	b1 a1 b2 a2  => left =a1 right= b2 => right -left = b2-a1 = ok
	b1 a1 a2 b2  => left =a1 right= a2 => right -left = a2-a1 = ok, a contained in b
	a1 b1 b2 a2  => left =b1 right= b2 => right -left = b2-b1 = ok, but b contained in a
	a1 b1 a2 b2  => left =b1 right= a2 => right -left = a2-b1 = ok
	a1 a2 b1 b2  => left =b1 right= a2 => right -left < 0 no overlap
*/
static inline int overlap_duration(int a1, int a2, int b1, int b2) {
	auto left = std::max(a1, b1);
	auto right = std::min(a2, b2);
	return right - left;
}

/*
	Used when creating/deleting a recording: lookup up corresponding epg record in the database;
	When called from channel_epg, k will point to an existing epg_record whose event_id will match,
	but which may have a slightly changed start_time, event_name...

	When called due to manually creating a recording, event_id will be TEMPLATE_EVENT_ID (0xffffff).
	In this case, we match when epg record is mostly contained within k's duration

	The search range is limited by tolerance to avoid excessive searching

*/
std::optional<epgdb::epg_record_t> epgdb::best_matching(db_txn& txnepg, const epgdb::epg_key_t& k, time_t end_time,
																												int tolerance) {
	/* we wish to find a record for record.k.service with lower start_time (in case start_time has changed)
	 */
	auto c = epgdb::epg_record_t::find_by_key(
		txnepg,
		k.service,								// service must match
		k.start_time - tolerance, // only consider records with close enough start_time
		find_geq,
		epgdb::epg_record_t::partial_keys_t::service // iterator will return only records on service
		);
	if (!c.is_valid())
		return {}; // no suitable records
	for (const auto& old : c.range()) {
		assert(old.k.service == k.service);
		if (old.k.event_id == TEMPLATE_EVENT_ID)
			continue;
		if (old.k.event_id == k.event_id) {
			return old; // exact match; impossible if k.event_id == TEMPLATE_EVENT_ID
		}
		if (k.event_id != TEMPLATE_EVENT_ID) {
			if (old.k.start_time > k.start_time + tolerance) // too large difference in start time
				return {};																		 // all records processed
		} else {
			if (old.k.start_time > end_time) // no time overlap possible for next records
				return {};										 // all records processed

			auto overlap = overlap_duration(k.start_time, end_time, old.k.start_time, old.end_time);
			auto duration = old.end_time - old.k.start_time;
			// overlap is enough if at most 20 minutes difference
			// note that this is only done for template matches
			if (duration - overlap < std::max(20 * 60, int(0.1 * duration)))
				return old;
		}
	}
	// no record was found in the database, so it must be a new one
	return {};
}

std::optional<epgdb::epg_record_t> epgdb::running_now(db_txn& txnepg, const chdb::service_key_t& service_key,
																											time_t now) {
	// const int tolerance = 30*60;
	/*
		find a record with start time equal to now, or the closest earlier start_time if none exists
	*/
	auto c = epgdb::epg_record_t::find_by_key(txnepg, service_key, now /* - tolerance*/, find_leq,
																						epgdb::epg_record_t::partial_keys_t::service);
	if (c.is_valid() && c.current().k.service != service_key)
		c.next(); // the current service has no records, or no records old enough
	if (c.is_valid())
		for (const auto& rec : c.range()) {

			if (rec.k.service != service_key) {
				assert(0);
				break; // we passed the current service
			}
			if (rec.k.start_time > now)
				return {}; // all records processed

			if (rec.end_time > now)
				return rec;
		}
	// no record was found in the database, so it must be a new one
	return {};
}

/*
	Find a service corresponding to an epg record.
	This amounts to finding the unknown extra_id in service.k.mux

	txn: transaction on channel database
	epg_record: record for which to find a proper service
*/

std::optional<chdb::service_t> epgdb::service_for_epg_record(db_txn& txn, const epgdb::epg_record_t& epg_record) {
	using namespace chdb;
	const auto& service_key = epg_record.k.service;
	auto c = chdb::service_t::find_by_key(txn, service_key.mux, service_key.service_id);
	if(c.is_valid())
		return c.current();
	return {}; // no result
}

std::unique_ptr<epg_screen_t> epgdb::chepg_screen(db_txn& txnepg,
																									std::shared_ptr<neumodb_t> tmpdb, uint32_t sort_order,
																									const chdb::service_key_t& service_key,
																									time_t start_time,
#ifdef USE_END_TIME
																									time_t end_time,
#endif
																									const ss::vector_<field_matcher_t>* field_matchers_,
																									const epgdb::epg_record_t* match_data_,
																									const ss::vector_<field_matcher_t>* field_matchers2_,
																									const epgdb::epg_record_t* match_data2_) {
	auto start_time_ = system_clock_t::from_time_t(start_time);
	epg_record_t prefix;
	prefix.k.service = service_key;
	auto cur = running_now(txnepg, service_key, start_time_);
	prefix.k.start_time = cur ? cur->k.start_time : start_time;
	auto lower_limit = prefix;
#ifdef USE_END_TIME
	decltype(lower_limit)* upper_limit = nullptr;
	if (end_time > start_time) {
		prefix.k.start_time = end_time;
		upper_limit = &prefix;
	}
#endif
	if (!tmpdb.get()) {
		tmpdb = std::make_shared<epgdb_t>(/*readonly*/ false, /*is_temp*/ true);
		tmpdb->add_dynamic_key(dynamic_key_t(sort_order));
		tmpdb->open_temp("/tmp/neumolists");
	}

	return std::make_unique<epg_screen_t>(txnepg, tmpdb, sort_order,
																				epg_record_t::partial_keys_t::service,
																				&prefix,
																				&lower_limit,
#ifdef USE_END_TIME
																				upper_limit,
#endif
																				field_matchers_,
																				match_data_,
																				field_matchers2_,
																				match_data2_

		);
}

void epgdb::gridepg_screen_t::remove_service(const chdb::service_key_t& service_key) {
	for (auto& e : entries) {
		if (e.service_key == service_key) {
			bool del = 1;
			if (e.epg_screen) {
				dtdebugf("GRID: remove epg for {}", service_key);
				e.epg_screen->drop_temp_table(del);
				e.epg_screen.reset();
				e.service_key = chdb::service_key_t();
			} else {
				dterrorf("GRID: attempting to remove non-existing epgscreen for {}", service_key);
			}
		}
	}
}

epgdb::epg_screen_t* epgdb::gridepg_screen_t::epg_screen_for_service(const chdb::service_key_t& service_key) {
	for (auto& e : entries) {
		if (e.service_key == service_key)
			return e.epg_screen.get();
	}
	return nullptr;
}

epgdb::epg_screen_t* epgdb::gridepg_screen_t::add_service(db_txn& txnepg, const chdb::service_key_t& service_key) {
	auto start_time_ = system_clock_t::to_time_t(start_time);
#ifdef USE_END_TIME
	auto end_time_ = system_clock_t::to_time_t(end_time);
#endif

	auto make_db = [this]() {
		if (tmpdb.get()) {
			std::shared_ptr<neumodb_t> new_tmpdb = std::make_shared<epgdb_t>(*tmpdb);
			new_tmpdb->add_dynamic_key(dynamic_key_t(this->epg_sort_order));
			ss::string<32> name;
			name.format("{:p}", fmt::ptr(new_tmpdb.get()));
			new_tmpdb->open_secondary(name.c_str());
			return new_tmpdb;
		} else {
			tmpdb = std::make_shared<epgdb_t>(/*readonly*/ false, /*is_temp*/ true);
			tmpdb->add_dynamic_key(dynamic_key_t(this->epg_sort_order));
			tmpdb->open_temp("/tmp/neumolists");
			return tmpdb;
		}
	};

	for (auto& e : entries) {
		if (e.epg_screen.get() == nullptr) {
			e.service_key = service_key;
			dtdebugf("GRID: add epg for {}", service_key);
			e.epg_screen = chepg_screen(txnepg,
																	make_db(), epg_sort_order,
																	service_key, start_time_
#ifdef USE_END_TIME
																	, end_time_
#endif
				);
			return e.epg_screen.get();
		}
	}
	auto& e = entries.emplace_back(service_key);
	dterrorf("GRID: add epg for {}", service_key);
	e.epg_screen = chepg_screen(txnepg,
															make_db(),
															epg_sort_order,
															service_key, start_time_
#ifdef USE_END_TIME
															, end_time_
#endif
		);
	return e.epg_screen.get();
}

fmt::format_context::iterator
fmt::formatter<epg_source_t>::format(const epg_source_t& s, format_context& ctx) const
{
	auto sat = chdb::sat_pos_str(s.sat_pos);
	return fmt::format_to(ctx.out(), "{:s} - nid={:d} tsid={:d} {:s}[{:d}]",
												sat.c_str(), s.network_id, s.ts_id, to_str(s.epg_type),
												(int)s.table_id);
}

fmt::format_context::iterator
fmt::formatter<epg_key_t>::format(const epg_key_t& k, format_context& ctx) const {
	return fmt::format_to(ctx.out(), "{} [{:d}] {:%F %H:%M}", k.service, k.event_id, fmt::localtime(k.start_time));
}


fmt::format_context::iterator
fmt::formatter<epg_record_t>::format(const epg_record_t& epg, format_context& ctx) const {
	return fmt::format_to(ctx.out(), "{} - {:%H:%M}:{} {}", epg.k, fmt::localtime(epg.end_time),
												to_str(epg.rec_status), epg.event_name);
}

/*!
	returns true if update or new record was found

	A matching record is found if event_id is the same

	matches are only found if the new record has not moved more than tolerance seconds
	earlier or has not been delayed past its original end_time

*/

static bool save_epg_record_if_better_(db_txn& txnepg, const epgdb::epg_record_t& record,
																			 std::function<void(const epgdb::epg_record_t&)> update_input) {
	assert(record.k.event_id != TEMPLATE_EVENT_ID);
	assert(!record.k.anonymous);
	const int tolerance = 60 * 60; /*maximum amount by which start_times may differ for record
																	 to be considered as a possible update of old record
																 */
	/*
		find all records with old.k.start_time >= record.k.start_time - tolerance for current service.

		Result can be:
		1) !c.valid() => there are no such records, which means we consider record as new

		2) c.valid() => need to examine in more detail

	*/
	auto epg_key = record.k;
	epg_key.start_time -= tolerance;
	auto c = epgdb::epg_record_t::find_by_key(
		txnepg,
		epg_key.service,													 // epg service must match
		epg_key.start_time,
		find_geq, // start_time  must be within range
		// note the absence of event_id => we allow any event_id
		epgdb::epg_record_t::partial_keys_t::service // iterator will only return records with proper service
		);
	if (c.is_valid())
		for (const auto& old : c.range()) {
			assert ( old.k.anonymous == (old.k.event_id == TEMPLATE_EVENT_ID));
			if(old.k.anonymous)
				continue;
			assert(old.k.service == record.k.service); // sanity check

			if (old.k.start_time > record.k.start_time + tolerance) // out of search range
				break;																								// all records processed

			/*
				TODO:
				1) are there cases where no valid event_id is available?
				2) we could check for duplicate records with non matching event_id in a more clever way (e.g.,
				check overlap)
				However, all of this could also be checked at read time
			*/
			if (old.k.event_id == record.k.event_id) { // exact match
				update_input(old);
				if (is_same(old, record)) {
					return false; // no need to save; nothing changed
				} else {
					if (old.k != record.k) { // difference is due to start time
#ifdef TOTEST
						delete_record(c, old);
#else
						// Delete the old, stale record
						delete_record_at_cursor(c); // slightly faster
#endif
						put_record(txnepg, record);
					} else { // record will be updated
#if 0
						put_record_at_key(c, c.current_serialized_primary_key(), record);
#else
						update_record_at_cursor(c, record);
#endif
					}
					return true;
				}
			} else if (old.k.event_id > 0xffff
								 /*these events do not come from a dvb stream, but, e.g., from xmltv.
									 Rather than trying to reconcile these records here,
									 we treat this info as a separate epg source
									 @todo: implement a way to clean possible duplicates at read time
								 */
				) {
				continue;
			}
		}
	// no record was found in the database, so it must be a new one
	put_record(txnepg, record);
	return true;
}

bool epgdb::save_epg_record_if_better_update_input(db_txn& txnepg, epgdb::epg_record_t& record) {
	auto update_input = [&record](const epgdb::epg_record_t& old) {
		// update record with the richest possible data
		if (record.story.size() < old.story.size())
			record.story = old.story;
		if (record.event_name.size() < old.event_name.size())
			record.event_name = old.event_name;
	};
	return save_epg_record_if_better_(txnepg, record, update_input);
}
bool epgdb::save_epg_record_if_better(db_txn& txnepg, const epgdb::epg_record_t& record) {
	auto update_input = [](const epgdb::epg_record_t& old) {};
	return save_epg_record_if_better_(txnepg, record, update_input);
}



/*
	Update the recording status of epg record, but leave the rest of the record alone.
	This is used to show on the epg screens
*/
bool epgdb::update_epg_recording_status(db_txn& epgdb_wtxn, const epgdb::epg_record_t& epgrec) {
	assert( (epgrec.k.event_id == TEMPLATE_EVENT_ID) == epgrec.k.anonymous);

	auto c = epgdb::epg_record_t::find_by_key(epgdb_wtxn, epgrec.k);
	assert(c.is_valid());
	if(!c.is_valid())
		return true;
	auto existing = c.current();
	if (existing.rec_status != epgrec.rec_status) {
		assert(existing.k.anonymous == (existing.k.event_id == TEMPLATE_EVENT_ID));
		existing.rec_status = epgrec.rec_status;
		assert (!existing.k.anonymous);
		epgdb::update_record_at_cursor(c, existing);
	}
	return false;
}
