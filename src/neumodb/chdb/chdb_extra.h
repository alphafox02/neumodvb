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

#pragma once
#include <util/template_util.h>
#include <iostream>
#include <cstdlib>
#include <cmath>
#include <variant>

#include "neumodb/chdb/chdb_db.h"
#pragma GCC visibility push(default)

namespace devdb {
	struct lnb_t;
	struct lnb_network_t;
	enum class lnb_pol_type_t : int8_t;
};

namespace chdb {
	using namespace chdb;

	std::tuple<chdb::sat_band_t, chdb::sat_sub_band_t> sat_band_for_freq(int frequency);
	std::tuple<int32_t, int32_t> sat_band_freq_bounds(chdb::sat_band_t sat_band, chdb::sat_sub_band_t sub_band);

	using any_mux_t = std::variant<chdb::dvbs_mux_t, chdb::dvbc_mux_t, chdb::dvbt_mux_t>;
	bool has_epg_type(const chdb::any_mux_t& mux, chdb::epg_type_t epg_type);
	const mux_key_t* mux_key_ptr(const chdb::any_mux_t& key);
	const mux_key_t* mux_key_ptr(const chdb::any_mux_t&& key) =delete; //cannot be used with temporaries

	mux_key_t* mux_key_ptr(chdb::any_mux_t& mux);
	mux_key_t* mux_key_ptr(chdb::any_mux_t&& mux) = delete; //cannot be used with temporaries

	template<typename mux_t>
	inline const mux_key_t* mux_key_ptr(const mux_t& mux) { return &mux.k;}

	const mux_common_t* mux_common_ptr(const chdb::any_mux_t& key);
	mux_common_t* mux_common_ptr(chdb::any_mux_t& key);
	bool put_record(db_txn&txn, const chdb::any_mux_t& mux, unsigned int put_flags=0);
	void delete_record(db_txn&txn, const chdb::any_mux_t& mux);


  /*
		returns true if epg type was actually updated
	*/
	bool add_epg_type(chdb::any_mux_t& mux, chdb::epg_type_t tnew);

	/*
		returns true if epg type was actually updated
	*/
	bool remove_epg_type(chdb::any_mux_t& mux, chdb::epg_type_t tnew);


	enum class update_mux_ret_t : int {
		UNKNOWN, //not in db
		MATCHING_KEY_AND_FREQ, //network_id, ts_id and sat_pos match, and frequencsy is close
		MATCHING_FREQ, //a mux exist with close frequenct, but with wrong network_id, ts_id
		NO_MATCHING_KEY, /*to save the mux, we would have to change the key, but this is not allowed
											 by caller, and this mux is not a template*/
		NEW, //the mux is new
		EQUAL //the mux exists and matches also in modulation parameters
	};


	namespace update_mux_preserve_t {
		enum flags : int {
			NONE = 0x0,
			SCAN_DATA  = 0x1,
			SCAN_STATUS  = 0x2,
			NUM_SERVICES  = 0x4, //directly used
			EPG_TYPES   = 0x8, // directly used
			NIT_SI_DATA = 0x10,
			SDT_SI_DATA = 0x20,
			MUX_COMMON = SCAN_DATA | SCAN_STATUS | NUM_SERVICES | EPG_TYPES | NIT_SI_DATA |SDT_SI_DATA,

			MUX_KEY = 0x40, //directly used
			TUNE_DATA = 0x80,
			MTIME = 0x100,

			ALL = 0xffff,
		};
	};

	using  update_mux_cb_t = std::function<bool(chdb::mux_common_t*, chdb::mux_key_t*,
		const chdb::mux_common_t*, const chdb::mux_key_t*)>;
	/*
		if callback returns false; save is aborted
		if callback receives nullptr, record was not found
	*/
	update_mux_ret_t update_mux(db_txn&txn, chdb::any_mux_t& mux,
															system_time_t now, update_mux_preserve_t::flags preserve, update_mux_cb_t cb,
																	/*bool ignore_key,*/ bool ignore_t2mi_pid, bool must_exist);

	inline update_mux_ret_t update_mux(db_txn&txn, chdb::any_mux_t& mux,
																		 system_time_t now, update_mux_preserve_t::flags preserve,
																		 /*bool ignore_key,*/ bool ignore_t2mi_pid, bool must_exist) {
		return update_mux(txn, mux, now, preserve,
											[](chdb::mux_common_t*, chdb::mux_key_t*,
												 const chdb::mux_common_t*, const chdb::mux_key_t*) { return true;}, /*ignore_key,*/
											ignore_t2mi_pid, must_exist);
	}

	template <typename mux_t> void clear_all_streams_pending_status(db_txn& chdb_wtxn,
																																	system_time_t now_, const mux_t& mux);

	inline void clear_all_streams_pending_status(db_txn& chdb_wtxn, system_time_t now_, const chdb::any_mux_t& mux) {
		std::visit([&](auto& mux){
			clear_all_streams_pending_status(chdb_wtxn, now_, mux);
		},mux);
	}

	/*! Put a mux record, taking into account that its key may have changed
		returns: true if this is a new mux (first time scanned); false otherwise
		if callback returns false; save is aborted
		if callback receives nullptr, record was not found

	*/
	template<typename mux_t>
	update_mux_ret_t update_mux(db_txn& txn, mux_t& mux,  system_time_t now, update_mux_preserve_t::flags preserve,
															update_mux_cb_t cb,
															/*bool ignore_key,*/ bool ignore_t2mi_pid, bool must_exist);

	template<typename mux_t>
	update_mux_ret_t update_mux(db_txn& txn, mux_t& mux,  system_time_t now, update_mux_preserve_t::flags preserve,
																	/*bool ignore_key,*/ bool ignore_t2mi_pid, bool must_exist) {
		return update_mux(txn, mux, now, preserve, [](chdb::mux_common_t*, chdb::mux_key_t*,
																									const chdb::mux_common_t*, const chdb::mux_key_t*) { return true;},
													/*ignore_key,*/ ignore_t2mi_pid, must_exist);
	}


	template<typename mux_t>
	inline bool is_template(const mux_t& mux) {
		return mux.c.tune_src == tune_src_t::TEMPLATE;
	}

	inline bool is_template(const chdb::any_mux_t& mux) {
		return mux_common_ptr(mux)->tune_src == tune_src_t::TEMPLATE;
	}

	inline bool is_template(const chg_t& chg) {
		return chg.k.bouquet_id == bouquet_id_template;
	}

	inline bool is_template(const chgm_t& chgm) {
		return chgm.k.channel_id == channel_id_template;
	}

	int32_t make_unique_id(db_txn& txn, chdb::chg_key_t key);
	int32_t make_unique_id(db_txn& txn, chdb::chgm_key_t key);

	template<typename T>
	requires (is_same_type_v<T, chdb::dvbs_mux_t> || is_same_type_v<T, chdb::dvbc_mux_t>
						|| is_same_type_v<T, chdb::dvbt_mux_t>)
		void make_mux_id(db_txn& txn, T& t );

	void make_mux_id(db_txn& rtxn, chdb::any_mux_t& mux);

	template<typename T>
	inline void make_unique_if_template(db_txn& txn, T& t );

	/*
		If the mux is a template (mux.k.network_id==0 && mux.k.mux.ts_id==and not yet has
		an extra_id (mux.k.extra_id == 0), then assign it a
		unique extra_id
	*/
	template<typename mux_t>
	inline void make_unique_if_template(db_txn& txn, mux_t& mux ) {
		if(is_template(mux)/* && mux.k.mux_id==0*/) {
			mux.k.mux_id = 0;
			chdb::make_mux_id<mux_t>(txn, mux);
		}
	}

	template<>
	inline void make_unique_if_template<chg_t>(db_txn& txn, chg_t& chg ) {
		if(is_template(chg))
			chg.k.bouquet_id = chdb::make_unique_id(txn, chg.k);
	}

	template<>
	inline void make_unique_if_template<chgm_t>(db_txn& txn, chgm_t& chgm) {
		if(is_template(chgm))
			chgm.k.channel_id = chdb::make_unique_id(txn, chgm.k);
	}

	chdb::media_mode_t media_mode_for_service_type(uint8_t service_type);

	std::tuple<std::optional<chdb::dvbs_mux_t>, std::optional<chdb::sat_t>>
	select_sat_and_reference_mux(db_txn& rtxn, const devdb::lnb_t& lnb,
															 const chdb::dvbs_mux_t* proposed_mux);

	chdb::dvbs_mux_t
	select_reference_mux(db_txn& chdb_rtxn, const devdb::lnb_t& lnb, int16_t sat_pos);

	std::optional<chdb::sat_t>
	select_sat_for_sat_band(db_txn& chdb_rtxn, const chdb::sat_band_t& sat_band, int sat_pos);

	inline bool scan_in_progress(const chdb::scan_id_t& scan_id) {
		return scan_id.subscription_id >= 0;
	}



};

namespace chdb {
	using namespace chdb;

	inline const char* pol_str(const fe_polarisation_t& pol) {
		return
			pol == fe_polarisation_t::H	 ? "H"
			: pol == fe_polarisation_t::V ? "V"
			: pol == fe_polarisation_t::L ? "L"
			: "R";
	}

	void sat_pos_str(ss::string_& s, int position);

	inline auto sat_pos_str(int position) {
		ss::string<8> s;
		sat_pos_str(s, position);
		return s;
	}

	void matype_str(ss::string_& s, int16_t matype, int rolloff=-1);
	inline auto matype_str(int16_t matype, int rolloff=-1) {
		ss::string<32> s;
		matype_str(s, matype, rolloff);
		return s;
	}

	inline bool is_same(const chgm_t &a, const chgm_t &b) {
		if (!(a.k == b.k))
			return false;
		if (!(a.chgm_order == b.chgm_order))
			return false;
		if (!(a.user_order == b.user_order))
			return false;
		if (!(a.media_mode == b.media_mode))
			return false;
		if (!(a.name == b.name))
			return false;
		return true;
	}

	bool is_same(const dvbs_mux_t &a, const dvbs_mux_t &b);
	bool is_same(const dvbc_mux_t &a, const dvbc_mux_t &b);
	bool is_same(const dvbt_mux_t &a, const dvbt_mux_t &b);
	bool tuning_is_same(const dvbs_mux_t& a, const dvbs_mux_t& b);
	bool tuning_is_same(const dvbc_mux_t& a, const dvbc_mux_t& b);
	bool tuning_is_same(const dvbt_mux_t& a, const dvbt_mux_t& b);

}

namespace chdb::sat {
	chdb::band_scan_t& band_scan_for_pol_sub_band(chdb::sat_t& sat, chdb::fe_polarisation_t pol,
																								chdb::sat_sub_band_t sub_band);

	void clean_band_scan_pols(chdb::sat_t& sat, devdb::lnb_pol_type_t lnb_pol_type);
/*!
		find a satellite which is close to position; returns the best match
		We adopt a tolerance of sat_pos_tolerance.
	*/

	inline auto find_by_position_fuzzy(db_txn& txn, int position, int tolerance = sat_pos_tolerance) {
		using namespace chdb;
		auto c = sat_t::find_by_key(txn, position, find_leq);
		if (!c.is_valid()) {
			c.close();
			return c;
		}
		int best =std::numeric_limits<int>::max();

		for(auto const& sat: c.range()) {
			//@todo double check that searching starts at a closeby cursor position
			if (sat.sat_pos == position) {
				return c;
			}
			if (position - sat.sat_pos   > tolerance)
				continue;
			if (sat.sat_pos - position > tolerance)
				break;
			auto delta = std::abs(sat.sat_pos - position);
			if (delta> best) {
				c.prev();
				return c;
			}
			best = delta;
		}
		c.close();
		return c;
	}
};

namespace chdb {

	/* tuning parameters (sat_pos, polarisation, frequency) indicate "equal or overlapping" muxes
	 */
	bool matches_physical_fuzzy(const dvbs_mux_t& a, const dvbs_mux_t& b, bool check_sat_pos=true,
															bool ignore_t2mi_pid=false);
	bool matches_physical_fuzzy(const dvbc_mux_t& a, const dvbc_mux_t& b, bool check_sat_pos=true,
															bool ignore_t2mi_pid=false);
	bool matches_physical_fuzzy(const dvbt_mux_t& a, const dvbt_mux_t& b, bool check_sat_pos=true,
															bool ignore_t2mi_pid=false);
	bool matches_physical_fuzzy(const any_mux_t& a, const any_mux_t& b, bool check_sat_pos=true,
															bool ignore_t2mi_pid=false);

	/* tuning parameters (sat_pos, polarisation, frequency) indicate muxes with same bandwidth
		 and frequency with tight tolerance
	*/
	bool matches_physical(const dvbs_mux_t& a, const dvbs_mux_t& b, bool check_sat_pos, bool ignore_stream_id);
	bool matches_physical(const dvbc_mux_t& a, const dvbc_mux_t& b, bool check_sat_pos, bool ignore_stream_id);
	bool matches_physical(const dvbt_mux_t& a, const dvbt_mux_t& b, bool check_sat_pos, bool ignore_stream_id);
	bool matches_physical(const any_mux_t& a, const any_mux_t& b, bool check_sat_pos, bool ignore_stream_id);

	inline bool is_same_stream(mux_key_t a , const mux_key_t& b) {
		a.t2mi_pid = b.t2mi_pid;
		if(a.mux_id == 0 || b.mux_id==0) //template
			a.mux_id = b.mux_id;
		return a == b;
	}

	inline int dvb_type(const chdb::any_mux_t& mux) {
		auto sat_pos = chdb::mux_key_ptr(mux)->sat_pos;
		if (sat_pos == sat_pos_dvbc || sat_pos == sat_pos_dvbt)
			return sat_pos;
		else
			return sat_pos_dvbs;
	}



	inline bool usals_is_close(int sat_pos_a, int sat_pos_b) {
		return std::abs(sat_pos_a-sat_pos_b) <= 100;
	}

	/*!
		find a mux for which the key is already known
	*/
	template<typename mux_t>
	requires (is_same_type_v<mux_t, chdb::dvbs_mux_t> || is_same_type_v<mux_t, chdb::dvbc_mux_t>
						|| is_same_type_v<mux_t, chdb::dvbt_mux_t>)
	db_tcursor<mux_t> find_by_mux(db_txn& txn, const mux_t& mux);

/*!
	find a matching mux, based on sat_pos, ts_id, network_id, ignoring  extra_id
	This is called by the SDT_other parsing code and will not work if multiple
	muxes exist on the same sat with the same (network_id, ts_id)
*/
	struct get_by_nid_tid_unique_ret_t {
		enum unique_type_t {
			UNIQUE,
			UNIQUE_ON_SAT,
			NOT_UNIQUE,
			NOT_FOUND
		};
		chdb::any_mux_t mux;
		unique_type_t unique{NOT_FOUND};
	};

	get_by_nid_tid_unique_ret_t get_by_nid_tid_sat_unique(db_txn& txn,  uint16_t network_id, uint16_t ts_id,
																												int16_t tuned_sat_pos);
	template<typename mux_t>
	db_tcursor<mux_t> find_by_mux_physical(db_txn& txn, const mux_t& mux, bool ignore_stream_id,
																				 /*bool ignore_keys,*/ bool ignore_t2mi_pid);

	std::optional<chdb::any_mux_t> get_by_mux_physical(db_txn& txn, chdb::any_mux_t& mux, bool ignore_stream_id,
																										 /*bool ignore_key,*/ bool ignore_t2mi_pid);

	void clean_scan_status(db_txn& wtxn);
	void clean_expired_services(db_txn& wtxn, std::chrono::seconds age);
	void clean_chgms_without_services(db_txn& wtxn);
};

namespace chdb::dvbs_mux {
	/*!
		return all sats in use by muxes
	*/
	ss::vector_<int16_t> list_distinct_sats(db_txn &txn);

}




namespace chdb {

	template<typename mux_t>
	requires (!is_same_type_v<mux_t, chdb::dvbs_mux_t>)
	db_tcursor_index<mux_t>
	find_by_freq_fuzzy(db_txn& txn, uint32_t frequency, int tolerance=1000);

	db_tcursor_index<chdb::dvbs_mux_t>
	find_by_mux_fuzzy(db_txn& txn, const chdb::dvbs_mux_t& mux, bool ignore_stream_ids, bool ignore_t2mi_pid);

	inline bool is_t2mi_mux(const chdb::any_mux_t& mux) {
		const auto *dvbs_mux =  std::get_if<chdb::dvbs_mux_t>(&mux);
		return dvbs_mux && (dvbs_mux->k.t2mi_pid > 0);
	}
};

namespace chdb::dvbt_mux {

	/*!
		find a mux which with the correct network_id and ts_id and closely matching frequency
	*/
	db_tcursor<chdb::dvbt_mux_t> find_by_mux_key_fuzzy(db_txn& txn, const dvbt_mux_t& mux, int tolerance=1000);

	inline bool is_template(const dvbt_mux_t& mux)
	{
		return mux.c.tune_src == tune_src_t::TEMPLATE;
	}
}

namespace chdb::dvbc_mux {

	/*!
		find a mux which with the correct network_id and ts_id and closely matching frequency
	*/
	db_tcursor<chdb::dvbc_mux_t> find_by_mux_key_fuzzy(db_txn& txn, const dvbc_mux_t& mux, int tolerance=1000);

	inline bool is_template(const dvbc_mux_t& mux)
	{
		return mux.c.tune_src == tune_src_t::TEMPLATE;
	}
}

namespace chdb::service {
	inline auto find_by_mux_key_sid(db_txn &txn, const mux_key_t &mux_key, uint16_t service_id) {
		return service_t::find_by_key(txn, mux_key, service_id, find_eq);
	}

/*
	find first service on mux

#if 0
	@todo this is used to loop over all services on a mux, but how do we stop the iteration
	when the cursor reaches the next mux?
	Currently caller must handle this by checking for change in mux
	set_prefix_key is the solution
#else
above comment is probably no longer valid. todo has been solved?
#endif
*/
	inline auto find_by_mux_key(db_txn& txn, const mux_key_t& mux_key) {
		auto c = service_t::find_by_key(txn, mux_key, find_geq, service_t::partial_keys_t::mux /*key_prefix*/);
		return c;
	}
}

namespace chdb {

	void merge_services(db_txn& wtxn, const mux_key_t& src_key, const any_mux_t& dst);
	void remove_services(db_txn& wtxn, const mux_key_t& mux_key);


	template<typename mux_t> float min_snr(const mux_t& mux);

	float min_snr(const chdb::any_mux_t& mux);

	std::optional<chdb::any_mux_t> find_mux_by_key(db_txn& txn, const chdb::mux_key_t& k);

	const char* lang_name(const language_code_t& code);
	inline bool is_same_language(language_code_t a, language_code_t b) {
		a.position =0;
		b.position =0;
		return a == b;
	}

	class history_mgr_t {
		bool inited=false;
		constexpr static int hist_size = 8;
		neumodb_t& db;
	public:
		chdb::browse_history_t h;

		history_mgr_t(neumodb_t& db_, int32_t user_id=0);
		void init();
		void clear();
		void save();
		void save(const service_t& service);
		void save(const chgm_t& channel);
		std::optional<chdb::service_t> last_service();
		std::optional<chdb::service_t> prev_service();
		std::optional<chdb::service_t> next_service();
		std::optional<chdb::service_t> recall_service();
		std::optional<chdb::chgm_t> last_chgm();
		std::optional<chdb::chgm_t> prev_chgm();
		std::optional<chdb::chgm_t> next_chgm();
		std::optional<chdb::chgm_t> recall_chgm();

	};

	delsys_type_t delsys_to_type(chdb::fe_delsys_t delsys);
	template<typename mux_t> inline constexpr delsys_type_t delsys_type_for_mux_type();

	template<> inline constexpr delsys_type_t delsys_type_for_mux_type<dvbs_mux_t>() { return  delsys_type_t::DVB_S;}
	template<> inline constexpr delsys_type_t delsys_type_for_mux_type<dvbc_mux_t>() { return  delsys_type_t::DVB_C;}
	template<> inline constexpr delsys_type_t delsys_type_for_mux_type<dvbt_mux_t>() { return  delsys_type_t::DVB_T;}


	bool bouquet_contains_service(db_txn& rtxn, const chdb::chg_t& chg, const chdb::service_key_t& service_key);

	bool toggle_service_in_bouquet(db_txn& wtxn, const chg_t& chg, const service_t& service);
	bool toggle_channel_in_bouquet(db_txn& wtxn, const chg_t& chg, const chgm_t& chgm);

}

namespace  chdb::service {
	void update_audio_pref(db_txn&txn, const chdb::service_t& service);
	void update_subtitle_pref(db_txn&txn, const chdb::service_t& service);
}

#define declfmt(t)																											\
	template <> struct fmt::formatter<t> {																\
	inline constexpr format_parse_context::iterator parse(format_parse_context& ctx) { \
		return ctx.begin();																									\
	}																																			\
																																				\
	format_context::iterator format(const t&, format_context& ctx) const ;\
}

declfmt(chdb::scan_status_t);
declfmt(chdb::scan_result_t);
declfmt(chdb::language_code_t);
declfmt(chdb::sat_sub_band_pol_t);
declfmt(chdb::band_scan_t);
declfmt(chdb::sat_t);
declfmt(chdb::dvbs_mux_t);
declfmt(chdb::dvbc_mux_t);
declfmt(chdb::dvbt_mux_t);
declfmt(chdb::any_mux_t);
declfmt(chdb::mux_key_t);
declfmt(chdb::service_t);
declfmt(chdb::service_key_t);
declfmt(chdb::fe_polarisation_t);
declfmt(chdb::chg_t);
declfmt(chdb::chgm_t);
declfmt(chdb::tune_src_t);
declfmt(chdb::key_src_t);
#if 0 //not implemented
declfmt(chdb::spectral_peak_t);
declfmt(chdb::mux_common_t);
declfmt(chdb::chg_key_t);
declfmt(chdb::chgm_key_t);
declfmt(chdb::browse_history_t);
#endif
#undef declfmt

#pragma GCC visibility pop
