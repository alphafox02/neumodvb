# Changes in neumoDVB #

## Changes in version neumodvb-1.0 ##

### Most important changes ###

* New database format: data related to local setup is now stored in anew database, called devdb.mdb
  Also, the definition of LNBs and frontends has changed to better support new features. As a result
  of the move, old LNB definitions will be lost and need to be reentered. The remaining database
  now contain data that is independent of the local hardware setup and can therefore be shared
  with other users.
* neumoDVB now makes better use of cards with and RF mux. These cards, such as
  TBS6909x and TBS6903x have multiple tuners (e.g., 4) and even more demodulators
  (e.g. 8). The RF mux allow connecting any demodulator to any tuner. This means that
  all demodulators can reach all connected satellite cables. Also, multiple muxes
  can share the same tuner and thus tune to multiple muxes in the same band and with the
  same polarisation simultaneously.
* neumoDVB can longer needs concepts like "slave tuners" because all tuners can use al RF inputs.
  So the concept of slave tuner has been removed.
* Parallel blind scan on supported cards, neumoDVB now uses all available demodulators
  to scan muxes. This makes blind scanning (almost) 8 times faster on supported cards
* Parallel SI scanning was already possible in neumoDVB, but now it can exploit more parallelism
  by setting the RF mux than before.
* Faster scanning: neumoDVB processes transponders with many (more than 200) multi-streams much faster
  by detecting streams which are not transport streams.
* Improved spectrum analysis: very wide band muxes are no longer detected as dozens of very small
  peaks, but as a single or a small number of peaks. This speeds up blind scanning as well. The estimated
  symbol rate of peaks used to be very inaccurate and is not more accurate.
* Change voltage from 0 to 18V in two steps to avoid current overloads when many diseqc switches switch
  simultaneously.

### Spectrum analysis and blind scan ###

* DVB-T frequency received from driver off by factor 1000.
* Parallel blind scan: on the spectrum dialog screen `Blind Scan all` now starts a parallel blind scan,
  using all adapters which can reach the selected LNB.
* The spectral peak analysis algorithm is now always performed by neumoDVB itself and the algorithm
  included in the drivers is ignored.
* New spectrum scan algorithm, missing fewer correct peaks and adding fewer incorrect peaks.
* SI Scanning code rewritten to avoid never ending scans and to make the overall process more efficient
  and tuning more responsive.  Specifically avoid trying to subscribe muxes after subscription on same
  sat band failed.
* Blind scan and regular SI scan code better integrated.
* For historic spectra, spectral peaks are always recomputed instead of loading them from disk.
  This allows taking advantage of newer (improved) analysis algorithms.
* Bug: signal_info poorly updated during spectrum scan.
* More efficient handling of newly discovered streams in multi-streams. If such streams are
  not transport streams, they are not scanned, but still entered in the database. When it is
  discovered that some streams have been removed, scanning thoese dead streams is prevented.
* Create new muxes for multi-streams as soon as they are detected before even tuning them.
* Improved multi-stream scanning: scan only dvb streams, but continue scanning for new matypes as long as
  new ones come in.
* Spectrum data is now indexed by key instead of by filename, eliminating confusion between spectra
  acquired within a very short time span.
* Bug: memory corruption in older spectral algorithms, leading to sporadic crashes.
* Issue #22: incorrect detrending with wideband LNB.
* The spectrum list now shows rf\_input instead of adapter\_no.
* Correctly show status of scan in progress in mux and service lists.
* Bug Fix scanning of DVB-C and DVB-T muxes caused by incorrect usage of matype
* Bug: error messages sometimes not shown when scanning fails
* Handle temporary failures during scanning. Such failures are caused by stid135 running out of LLR bandwidth.
* Improve the way signal info and scan notification are communicated to GUI.
* At startup, only clean mux pending/active status for dead pids, thus allowing multiple instances of neumoDVB
  running on the same computer and sharing resources.
* Ensure that merge_services is only called for dvb muxes; remove services.
  when it is detected that a dvb mux has been replaced with non DVB one.
* Disallow moving positioner during scan.
* When tuning fails set scan duration to tune time.
* Bug: frequencies are rounded to integer when shown in graph.
* Log lock time.
* When user presses abort tune while blind scan is in progress, stop blind scan as well.
* Continue blind scan properly when tuning fails, instead of hanging.

### frontend list

* Adapters and cards are now identified by a unique MAC address, which should avoid problems due to
  linux DVB adapter renumbering.
* Cards are now auto numbered. In the GUI C3 refers to card number 3.
  The main reason for this short card number is to refer to cards in the GUI using a small
  number instead of via a long MAC address.  The numbering remains
  stable when cards are removed and later reinstalled.
* Delivery systems can be disabled per adapter, e.g., to inform nuemoDVB that no DVB-T antenna
  is connected to a DVB-T/DVB-C card, but only a DVB-C-cable.
* Add subscription column, which shows the mux that is currently tuned.
* Various columns added to make it easier to distinghuish between cards of the same type.
* Distinguish between sweep and fft spectrum analysis capability.
* Various columns added to show features supported by adapters: blind scan, spectrum scan, multi-stream...
* Bug: incorrect detection of adapter presence and availability.

### LNB list ###
* LNBs are no longer coupled with frontends, but with card/rf\_in pairs. These can
  be selected from a popup menu, which onluy shows valid combinations.
* Change LNB key to card_mac_address, rf_input; add conversion script
* Bug: LNBlist screen corruption when no networks defined.
* Add can_subscribe_lnb_band_pol_sat and can_subscribe_dvbc_or_dvbt_mux.
* Bug: do not ignore LNBs on positioners which point to the correct sat when selecting and LNB for tuning.
* Bug: LNB incorrectly updated when frontends change or disappear.
* Add Ka-Band LNB definitions.
* Add wideband LNB definitions.
* Auto compute inversion based on LNB parameters.
* Skip unavailable LNBs during subscription.
* LNB naming includes card_no, and card_no, adapter name and adapter number are added as cached property.
* Add LOF low/high in LNB list


### Tuning and viewing ###

* Improved support for dvbapi
* Gradually change voltage from from 0 to 18V to avoid current overloads when many diseqc switches switch
  simultaneously.
* Wait 200ms after powering up diseqc circuitry.
* Handle invalid parameters during tuning (e.g., frequency/symbol_rate out of range), reporting them to
  GUI and properly releasing resources.
* Prevent forcing blind mode based on delsys; instead respect tune option.
* Split all tuning related actions into two phases: 1) reservation of resources; 2) the actual tuning
  This allows to better handle some failure cases.
* Subscriptions are now stored in the database, facilitating multiple instances of neumoDVB running parallel.
* Bug: diseqc commands sent without waiting for LNB power-up.
* Bug: tuning to DVB-C/DVB-T fails; invalid assertion.
* Bug: when tuning fails in positioner_dialog, subscription_id<0 is returned but mux is not unsubscribed (and
  cannot be unsubscribed).
* Bug: assertion when tuning mux with symbol_rate==0.
* Improve detection and handling of retune conditions; improved calling of in_scan_mux_end and
  on_notify_signal_info.
* Bug: confusion between DVB-C and DVB-S.
* Prefer to reuse current adapter when all else is equal.
* When two subscriptions use same tuner, do not power down tuner when ending only one of the subscriptions.
  This is supported as of neumo driver 1.5.
* Bug: voltage and tone state not cleared after frontend close, resulting in diseqc not being sent
  and tuning failing.
* Avoid crash on exit when fe_monitor not running.
* Assertion when softcam returns bad keys.
* Enable "tune add" command on service list screen, and not only on live screen.
* Bug: 2nd viewer window goes black when first is closed.
* Refactor get_isi_list; use matype_list when available.
* Get lock time and bitrate from driver; detect neumo api version.
* Bug: detected matype overwritten in some cases.

### SI processing ###

* Bug: incorrect skipping of stuffing table on 19.2E 10773H.
* Override SI-mux delsys from tuner (14.0W 11024H).
* If mux has no NIT and SDT still add services after SDT/NIT timeout. Happens on 14.0W 1647V.
* Bug: sat_pos wrong in pmt processing (14.0W).
* In case NIT data is obviously wrong, also fix polarisation, sat_pos and delivery system. Happens on 14.0W 11623V.
* Add special case for t2mi detection: 14.0W 11647V.
* In case NIT processing does not succeed, tuned_mux_key may be wrong and as a result SDT processing can
  conclude that we are on wrong sat leading to never ending scan (14.0W 11623V).
* If mux has no NIT and SDT still add services after SDT/NIT timeout. Happens on 14.0W 1647V
* Prevent never completing tables from not timing out.
* Add NOTS scan result to indicate that the mux is not a transport stream.
* Bug: sdt sometimes updates invalid mux.
* Correctly handle several cases on 30.0W where NIT and SDT disagree.
* Check for unlockable and non existing streams.
* Distinguish between non-locked muxed ans muxes with bad parameters that cause tuning failure.
* Retrieve signal_info when needed for si-processing from cache rather
  than synchronously retrieving it from driver (which stalls tuner thread).
* Bug: no mux_desc when adding a service found only in PMT.
* Process PMTs even in minimal scan.
* Prevent tables with persistent CRC errors from causing si scan to never complete.


### GUI related ###
* Save Usals location in database when user changes it (and reload from database) instead of storing
  usals location in read-only config file.
* Improved handling of illegal sort orders (no more assertion).
* Positioner dialog is now saved to database and no longer set in a config file.
* Show radio background for radio channels.
* Make page up/down work on numeric keypad.
* Display detected matype information.
* Positioner_dialog and spectrum_dialog: handle missing/incorrect data.
* Improved handling of failed edits.
* Improved handling of missing LNB data in GUI.
* Show DVB-C or DVB-T muxlist when user selects either of them on DVB-S muxlist.
* Add DVB-C and DVB-S to sat_list so that they can be selected on service screen; when
  selecting either on on DVB-S mux screen, the GUI switches to DVB=T or DVB-C mux screen accordingly.
* Bug: handle various cases of assertion when record is not found (due to other bugs).
* Add number of services to service, chgm screens and number of muxes to mux screen.
* Do not display -1 as stream_id in gui.
* Show tuned frequency also when there is no lock/.
* Show correct dB values in overlay when values reach maximum. (alternative for pr #23).
* Bug: Distinguish between SI table present and complete in GUI.
* Show more stream_ids.
* Show symbol_rate and frequency as soon as timing lock is achieved.
* Bug: incorrect reference row number after deleting record at reference cursor. The new code
  invalidates the cursor.
* Bug: incorrect row number updating of reference cursor while deleting records. This results in
  assertions being triggered and/or incorrect rows focused or displayed.
* Show error message when blind/spectrum scanning and drivers not installed.
* Report drivers not installed when user attempts to blind scan or spectrum scan.
* Bug: if current record does not exist, focus row 0 instead of -1

### Database and options ###

* Major database change: identify adapters by their mac address and no longer by adapter number.
  Limitations in the current database upgrade code result in the loss of all defined LNBs. Also,
  old spectra will not show the adapter on which they were captured.
* Split off lndb and fe database from chdb into devdb.
* Implement option merging when loading config files, thus adding options which are missing in user config file
* Clean expired services and channels which are more than one month old to avoid
  huge database.
* Clean subscriptions by dead processes in database.
* Clean channels which no longer have services.
* Add pyschemadb; proof of concept for reading non-upgraded db schema and data in pythhon test code.
* Add "neumodbstats.py" script which shows various statistics (number of records etc) of database records
* Avoid opening the same database twice. This prevents an assertion in mdb.c and leads to faster
  GUI.
* Proof of concept for reading database with outdated schema from python. This can be used to  convert old database
  formats in more flexible (but slower) ways.
* Report fatal lmdb errors on stderr.
* Fix neumoupgrade path issue.
* Bug: db_upgrade fails when database name has trailing slash.
* Increase default database mmap size, allowing databases to grow bigger if needed.
* Bug: erroneous assertion in cursor code.
* Bug: double abort in cursor code.
* Ensure all transactions are aborted.
* Bug: iterating over range fails when modifying records.
* Set proper key_prefix on find_... calls.
* Do not throw an exception when mdb_cursor_get returns EINVAL. This is needed when checking if the current
  cursor is still valid.
* Bug: continuing c.range() after cursor is made invalid.
* Add db_tcursor and db_tcursor_ move and copy assignment operators.
* Bug: source cursor not invalided in move assignment.
* Bug: MDB_GET_BOTH should be used when copying cursors with MDB_DUPSORT


### Various ###

* Ubuntu 22.4 compilation instructions.
* Ancient ubuntu: compilation fix.
* Bug: double abort after initializing sat_list.
* Delay removing active_adapters when interating over active_adapters.
* Bug: incorrect get_by_nit_tid_unique for dvbc and dvbt.
* Fix deadlocks because of multiple accesses to fe->ts by same thread.
* Bug: deadlock when adapter removed.
* Bug: resize_no_init for ss::string_ not adding trailing 0.
* Bug: lambda capture should store value instead of reference.


## Changes in version neumodvb-0.9 ##

SI-processing related

* Incorrect activation of PMT parsers
* Avoid showing incorrect SI data in tuned mux panel
* Faster detection of stable pat, resulting in faster SI scanning
* Better handle invalid SI information on 7.0E
* Handle SI-sections with different version numbers
* Also parse PMTs during regular SI scanning
* Avoid needless frequent epg scanning on services without epg

Spectrum and blind scanning

* When adapter is not available, show error message and gracefully end blindscan
* Properly handle multi-stream with the streams having the same network and ts id.
 These muxes would overwrite each other while scanning. Happens, e.g., on 14W.
* Avoid python back-traces when no peaks found in spectrum
* Fixed bug: when LNB changes due to clicking on a mux in the spectrum panel,
 the LNB select combobox does not show the newly selected LNB, which will be used for tuning
 but uses it anyway. This causes blind tunes to happen on unexpected LNBs
* Improvement: when the user loads a spectrum from file in spectrum scan, then selects a
 mux and blindscans, use the current LNB whenever possible, except if this one cannot
 tune the mux (wrong sat or wrong type of LNB). Only in that case, switch to the LNB originally used
 to capture the spectrum.
* Include not only hours and minutes but also seconds in names of files storing spectrum data. This
 solves the problem that spectrum acquisitions started within one minute would overwrite each other.
* The code now asks for a 50kHz resolution spectrum, leading to slightly slower scans in stid135.
 This detects more low symbol rate muxes.
* Fixed bug: DVBS2-QPSK streams incorrectly entered as DVBS1 streams in database
* Fixed bug: incorrect detection of roll-off parameters.
* More useful packet or bit error rate estimation. The new code measures errors before FEC/Viterbi/LDPC
 correction. This requires blindscan drivers with version > release.0.9.


Installation

* Prevent some files from installing

GUI

* Show disabled menu items as grayed out
* No longer use the single letters 'E' and 'C' as shortcuts, except in live mode
* Fixed bug that causes channels to scroll offscreen
* Fix bug that prevented proper navigation with arrow keys on EPG screen
* Fixed bug: onscreen display of SNR not working in radio mode
* Properly handle cases with unavailable SNR
* Fixed some layout bugs
* Add timing lock indicator (replaces pretty useless signal indicator)
* Immediately activate changes entered by user on "frontend list" screen. This is important
 when user enables/disables a frontend
* Add channel screenshot command
* Show more stream numbers in the positioner dialog and in the spectrum dialog on muxes with
 large number of streams

Compilation and internals

* Switch to clang20 by default except on "ancient Ubuntu" aka "Ubuntu LTS"
* Fix double close of cursors and incorrect freeing, leading to assertion failures
* Add command for building fedora rpms. Main problem to start really using this is a dependency
 on mpl-scatter-plot, which cannot be installed as an rpm
* Fix incorrect recompiling of pre-compiled headers with cmake > 3.19
* Removed dependency on setproctitle and made it less error-prone
* Add script for testing peak finding algorithm

Diseqc

* Add more time between sending commands to cascaded swicthes, solving some erroneous switching


## Changes in version neumodvb-0.8 ##

Installation related:

* Improved installation instructions for fedora 36 and Ubuntu 20.04 LTS.


Spectrum acquisition and blindscan related:

* Added Export command, which can export service, mux, ... lists.
* Allow selecting multiple muxes for scanning, instead of selecting them one at a time and pressing `Ctrl-S` each time
* Allow blind scanning non detected peaks by selecting a region of spectrum graph.
* Improved positioning of frequency/symbol rate annotations on the spectrum graph. The labels are better
 readable and use less vertical space, preventing the need for vertical resizing in many cases.
* Added predefined pls code for 33.0E (BulgariaSat).
* Avoid python exception when spectrum scan results in zero detected peaks
* Avoid confusion between embedded and non-embedded streams on same frequency leading to missing or overwritten
 muxes in the database
* Bug when multiple subscriptions use the same mux, but one of them uses a t2mi substream;
* Prevent scan hanging for ever on some muxes
* Ensure that scan status is properly handled with embedded streams to prevent scans that never finish;
* Data race when starting embedded_stream_reader, causing tsp sub-process to be launched multiple times.
* Incorrect scan result reported on t2mi stream because of incorrect lock detection
* Autodiscover t2mi streams on 40.0E (workaround for detecting incompliant t2is)
* Handle empty NIT_ACTUAL in embedded stream on 40.0E 3992L T2MI. This
 causes the ts_id and original_network_id from the embedded t2mi SDT
 not to be taken into account.
* When tuning to t2mi mux from database record, preserve original_network_id
 and ts_id in the embedded si
* Allow resetting LNB LOF offset


EPG and recording related:

* Fixed layout bugs in grid epg.
* Improved handling of 'anonymous' recordings. These are recordings created by the user by
  entering start and end time instead of recording an epg record. In the new code, these
  anonymous recordings will be kept  as instructed by the user, but also secondary recordings
  will be created for each epg record matching the time window. This is convenient for services
  with only now/next epg, which may arrive after scheduling the anonymous recording. Anonymous
  recordings will be shown on the EPG screen, but will be overlayed with epg records, should these
  exist. Canceling a secondary epg recording also cancels the anonymous recording.


Playback and viewing:

* During live viewing and recordings playback, replace the original PMT with a minimal PMT
  containing only the video stream, and current audio and subtitle stream. This should prevent
  playback problems of services on 30.0W which share the same PMT. mpv tends to get confused
  about the audio stream selection in this case. This should also fix the missing sound on
  Sport Italia HD (5.0W).
* Incorrect indication of live/timeshift/rec status in live overlay
* Hide snr and strength when playing back a recording.
* Reduce buffering in tsp sub process to avoid delay when live viewing t2mi services

Various bugs fixed:

* anonymous recordings 60 times too long.
* Cannot activate edit mode in lnb network list

## Changes in version neumodvb-0.7 ##

Positioner related

* More consistent layout of positioner dialog. Disable some functions when unusable
* Fixes for diseqc12, e.g., new diseqc12 value not stored when user updates it
* Positioner bug fixes: send diseqc switch commands before sending any positioner command;
  report better error messages in GUI; properly handle continuous motion.
* Send diseqc switch commands before spectrum scan to avoid scanning the wrong lnb
* Prevent dish movement during mux scan
* Satellite is now only shown as "confirmed" (no question mark) if the position was actually
  found in the NIT table.
* Positioner dialog: show SNR and constellation even when tuner is not locked
* Avoid interference between positioner dialog and mux scan
* Disallow starting positioner dialog from some screens, when context does not allow guessing which
  lnb the user wants to use
* In positioner dialog allow negative SNRs. Yes, there are muxes which lock with a negative SNR!
* Documentation of positioner commands
* Allow rotors which can rotate by more than 65 degrees. The old code used to cause a goto south
  in this case.

Scanning related:

* Mux tables now show the source of the mux information. For instance if the frequency
 was found in the NIT table or rather from the tuner and if sat position was guessed or
 found in NIT
* Improved handling of bad data while scanning muxes:
  0 frequency (7.3W 11411H) or other nonsensical values;
  contradictory information in muxes from 0.8W and 1.0W;
  invalid satellite positions;
  on 42.0E, muxes are being reported as from 42.0W;
  some muxes report AUTO for modulation
  incorrect polarisation reported in C-band reuters mux on 22W;
  incorrect polarisation reported on 7.3W 11411H
  22.0E 4181V and other muxes which claim QAM_AUTO in NIT
* Fixed incorrectly reported roll-offs (may require driver update)
* Correctly handle some cases where mux or blindscan never finish
* Remove "scan-in-progress" data from database at startup to avoid an old scan from
  restarting when neumoDVB is restarted
* Improved handling of muxes reported on nearby satellites (e.g., 0.8W and 1.0W). Avoid creating
  duplicates in this case. The downside is that when scanning e.g., 0.8W the found mux may
  appear in the list for 1.0W and thus confuse the user
* Fixed incorrect display of scan status on mux list when mux scan is in progress
* Fixed bug where incorrect pls_code and pls_mode was retrieved from driver
* Correctly save DVBS2 matype in the database and do not show this value for DVBS
* Fix incorrect lock detection
* When scanning multistreams: retain tuning info when scanning next stream
* Spectrum blindscan now moves faster to the next candidate peak when mux does not contain
  a DVB stream

t2mi related:

* Fixed corruption in t2mi streams. This requires a patched tsduck as well.
* Improved handling of non-t2mi DVB-T service information on DVB-S muxes. Avoid entering
  such muxes as DVB-T
* correctly handle duplicate packets in transport streams; tsduck needs to be patched
  to also handle t2mi streams correctly

GUI related
* Handle some corruption in service and mux list
* Various GUI improvements.
* Changed key-binding for activating edit-mode.
* New "status list" screen shows which adapters are active and what they are doing
* Fix some crashes when ending program
* Fix some errors when service list is empty
* Allow user to select a stream_id even when dvb streams reports incorrectly that stream is
  not multistream
* Correctly update recordings screen when database changes
* Minimum RF level shown on live screen is now lower than before
* Fixed some issues with list filtering

Other

* Fixed some bugs in the code used to look up muxes. For instance, in rare cases a mux with
  the wrong polarization was returned
* Fixed bug: lnb offset correction was applied in wrong direction on C band
* Detection of whether dish needs to be moved was sometimes incorrect; database now contains
  the ultimate truth on this.
* Fixes to support Ubuntu 20.04
* Fixed race between closing and then reopening the same frontend, which caused sporadic assertions.
* correctly release lnb in more cases then before: when user closwes window; when spectrum blindscan
  finishes
* various other bugs