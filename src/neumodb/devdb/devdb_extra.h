/*
 * Neumo dvb (C) 2019-2022 deeptho@gmail.com
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
#include <iostream>
#include <cstdlib>
#include <cmath>
#include <variant>
#include <optional>


#include "neumodb/devdb/devdb_db.h"
#include "neumodb/chdb/chdb_extra.h"
#pragma GCC visibility push(default)


unconvertable_int(int64_t, adapter_mac_address_t);
unconvertable_int(int64_t, card_mac_address_t);
unconvertable_int(int, adapter_no_t);
unconvertable_int(int, frontend_no_t);

namespace devdb {

	using namespace devdb;

	int16_t make_unique_id(db_txn& txn, devdb::lnb_key_t key);

	inline void make_unique_if_template(db_txn& txn, lnb_t& lnb ) {
		if(lnb.k.lnb_id<0)
			lnb.k.lnb_id = devdb::make_unique_id(txn, lnb.k);
	}

};

namespace devdb {
	using namespace devdb;

	void to_str(ss::string_& ret, const lnb_t& lnb);
	void to_str(ss::string_& ret, const lnb_key_t& lnb_key);
	void to_str(ss::string_& ret, const lnb_network_t& lnb_network);
	void to_str(ss::string_& ret, const fe_band_pol_t& band_pol);
	void to_str(ss::string_& ret, const fe_t& fe);
	void to_str(ss::string_& ret, const fe_key_t& fe_key);

	template<typename T>
	inline void to_str(ss::string_& ret, const T& t) {
	}


	template<typename T>
	inline auto to_str(T&& t)
	{
		ss::string<128> s;
		to_str((ss::string_&)s, (const T&) t);
		return s;
	}

	std::ostream& operator<<(std::ostream& os, const lnb_key_t& lnb_key);
	std::ostream& operator<<(std::ostream& os, const lnb_t& lnb);
	std::ostream& operator<<(std::ostream& os, const lnb_network_t& lnb_network);
	std::ostream& operator<<(std::ostream& os, const fe_band_pol_t& band_pol);
	std::ostream& operator<<(std::ostream& os, const chdb::fe_polarisation_t& pol);
	std::ostream& operator<<(std::ostream& os, const fe_key_t& fe_key);
	std::ostream& operator<<(std::ostream& os, const fe_t& fe);

}


namespace devdb::dish {
	//dish objects do not really exist in the database, but curent state (usals_pos) is stored in all relevant lnbs
	int update_usals_pos(db_txn& wtxn, int dish_id, int usals_pos);
	bool dish_needs_to_be_moved(db_txn& rtxn, int dish_id, int16_t sat_pos);
};


namespace devdb {

	bool lnb_can_tune_to_mux(const devdb::lnb_t& lnb, const chdb::dvbs_mux_t& mux, bool disregard_networks, ss::string_ *error=nullptr);

	struct resource_subscription_counts_t {
		int dish{0};
		int lnb{0};
		int rf_coupler{0};
		int tuner{0};
	};

}

namespace  devdb::lnb {

	std::tuple<bool, int, int, int>  has_network(const lnb_t& lnb, int16_t sat_pos);

	inline bool dish_needs_to_be_moved(const lnb_t& lnb, int16_t sat_pos) {
		auto [has_network_, priority, usals_move_amount, usals_pos] = has_network(lnb, sat_pos);
		return !has_network_ || usals_move_amount != 0 ;
	}

	const devdb::lnb_network_t* get_network(const lnb_t& lnb, int16_t sat_pos);
	devdb::lnb_network_t* get_network(lnb_t& lnb, int16_t sat_pos);

	chdb::dvbs_mux_t
	select_reference_mux(db_txn& rtxn, const devdb::lnb_t& lnb, const chdb::dvbs_mux_t* proposed_mux);

	devdb::lnb_t
	select_lnb(db_txn& rtxn, const chdb::sat_t* sat, const chdb::dvbs_mux_t* proposed_mux);

	/*
		band = 0 or 1 for low or high (22Khz off/on)
		voltage = 0 (V,R, 13V) or 1 (H, L, 18V) or 2 (off)
		freq: frequency after LNB local oscilllator compensation
	*/
	std::tuple<int, int, int> band_voltage_freq_for_mux(const devdb::lnb_t& lnb, const chdb::dvbs_mux_t& mux);
	devdb::fe_band_t band_for_freq(const devdb::lnb_t& lnb, uint32_t frequency);

	inline devdb::fe_band_t band_for_mux(const devdb::lnb_t& lnb, const chdb::dvbs_mux_t& mux) {
		return band_for_freq(lnb, mux.frequency);
	}

	int voltage_for_pol(const devdb::lnb_t& lnb, const chdb::fe_polarisation_t pol);

  /*
		translate driver frequency to real frequency
		tone = 0 if off
		voltage = 1 if high
		@todo: see linuxdvb_lnb.c for more configs to support
		@todo: uniqcable
	*/
	int freq_for_driver_freq(const devdb::lnb_t& lnb, int frequency, bool high_band);
	int driver_freq_for_freq(const devdb::lnb_t& lnb, int frequency);
	std::tuple<int32_t, int32_t, int32_t> band_frequencies(const devdb::lnb_t& lnb, devdb::fe_band_t band);

	bool add_network(devdb::lnb_t& lnb, devdb::lnb_network_t& network);
	void update_lnb(db_txn& wtxn, devdb::lnb_t&  lnb);
	void reset_lof_offset(devdb::lnb_t&  lnb);
	std::tuple<uint32_t, uint32_t> lnb_frequency_range(const devdb::lnb_t& lnb);

	bool can_pol(const devdb::lnb_t &  lnb, chdb::fe_polarisation_t pol);
	chdb::fe_polarisation_t pol_for_voltage(const devdb::lnb_t& lnb, int voltage);
	inline bool swapped_pol(const devdb::lnb_t &  lnb) {
		return lnb.pol_type == devdb::lnb_pol_type_t::VH || lnb.pol_type == devdb::lnb_pol_type_t::RL;
	}

	void update_lnb_adapter_fields(db_txn& wtxn, const devdb::fe_t& fe);
	void on_mux_key_change(db_txn& wtxn, const chdb::dvbs_mux_t& old_mux, chdb::dvbs_mux_t& new_mux,
												 system_time_t now_);
	std::optional<devdb::rf_coupler_t> get_rf_coupler(db_txn& rtxn, const devdb::lnb_key_t& lnb_key);
	int rf_coupler_id(db_txn& rtxn, const devdb::lnb_key_t& key);

	inline bool can_move_dish(const devdb::lnb_t& lnb) {
		switch(lnb.rotor_control) {
		case devdb::rotor_control_t::ROTOR_MASTER_USALS:
		case devdb::rotor_control_t::ROTOR_MASTER_DISEQC12:
			return true; /*this means we will send usals commands. At reservation time, positioners which
										 will really move have already been penalized, compared to positioners already on the
												correct sat*/
			break;
		default:
			return false;
		}
	}

	inline bool on_positioner(const devdb::lnb_t& lnb)
	{
		switch(lnb.rotor_control) {
		case devdb::rotor_control_t::ROTOR_MASTER_USALS:
		case devdb::rotor_control_t::ROTOR_MASTER_DISEQC12:
		case devdb::rotor_control_t::ROTOR_SLAVE:
			return true;
			break;
		default:
			return false;
		}
	}
}

namespace devdb::fe {
	std::optional<devdb::fe_t>
	find_best_fe_for_lnb(db_txn& rtxn, const devdb::lnb_t& lnb,
											 const devdb::fe_key_t* fe_to_release,
											 bool need_blindscan, bool need_spectrum, bool need_multistream,
											 chdb::fe_polarisation_t pol, fe_band_t band,
											 int usals_pos);

	std::optional<devdb::fe_t>
	find_best_fe_for_dvtdbc(db_txn& rtxn,
													const devdb::fe_key_t* fe_to_release,
													bool need_blindscan, bool need_spectrum, bool need_multistream,
													chdb::delsys_type_t delsys_type);

	std::tuple<std::optional<devdb::fe_t>,
						 std::optional<devdb::lnb_t>,
						 resource_subscription_counts_t>
	find_fe_and_lnb_for_tuning_to_mux(db_txn& rtxn,
																		const chdb::dvbs_mux_t& mux, const devdb::lnb_t* required_lnb,
																		const devdb::fe_key_t* fe_key_to_release,
																		bool may_move_dish, bool use_blind_tune,
																		int dish_move_penalty, int resource_reuse_bonus);

	resource_subscription_counts_t subscription_counts(db_txn& rtxn, const lnb_key_t& lnb_key);

	bool is_subscribed(const fe_t& fe);

	inline bool has_rf_in(const fe_t& fe, int rf_in) {
		for(auto& r: fe.rf_inputs) {
			if (r == rf_in)
				return true;
		}
		return false;
	}

	inline bool suports_delsys_type(const devdb::fe_t& fe, chdb::delsys_type_t delsys_type) {
		for (auto d: fe.delsys) {
			if (chdb::delsys_to_type(d) == delsys_type)
				return  true;
		}
		return false;
	}

	int unsubscribe(db_txn& wtxn, const fe_key_t& fe_key, fe_t* fe_ret=nullptr);
	int unsubscribe(db_txn& wtxn, fe_t& fe);

	int reserve_fe_lnb_band_pol_sat(db_txn& wtxn, devdb::fe_t& fe, const devdb::lnb_t& lnb,
																	devdb::fe_band_t band,  chdb::fe_polarisation_t pol, int frequency);


	int reserve_fe_lnb_exclusive(db_txn& wtxn, devdb::fe_t& fe, const devdb::lnb_t& lnb);
	int reserve_fe_dvbc_or_dvbt_mux(db_txn& wtxn, devdb::fe_t& fe, bool is_dvbc, int frequency);

	template<typename mux_t>
	std::optional<devdb::fe_t>
	subscribe_dvbc_or_dvbt_mux(db_txn& wtxn, const mux_t& mux, const devdb::fe_key_t* fe_key_to_release,
														 bool use_blind_tune);

	std::tuple<std::optional<devdb::fe_t>, std::optional<devdb::lnb_t>, resource_subscription_counts_t>
	subscribe_lnb_band_pol_sat(db_txn& wtxn, const chdb::dvbs_mux_t& mux,
																 const devdb::lnb_t* required_lnb, const devdb::fe_key_t* fe_key_to_release,
																 bool use_blind_tune, int dish_move_penalty, int resource_reuse_bonus);
	std::optional<devdb::fe_t>
	subscribe_lnb_exclusive(db_txn& wtxn,  const devdb::lnb_t& lnb, const devdb::fe_key_t* fe_key_to_release,
													bool need_blind_tune, bool need_spectrum);
	devdb::fe_t subscribe_fe_in_use(db_txn& wtxn, const fe_key_t& fe_key);

};

#pragma GCC visibility pop