# Phase 0 — usage map and deletion proposal

No application source, notebook, processed table, model, or existing report was changed. This document is the review artifact. All ten nonempty source files were read before this audit. Notebook code cells were inspected as consumers; stored notebook output is not evidence of current execution. Cell numbers below are zero-based JSON cell indexes.

## Execution and scope

Executed all data-building functions and recommendation preparation, matrix fitting, neighbor fitting, candidate/pair/profile/sample generation in memory using the existing virtual environment. Did not call save_data, save_check, audit_data, save_artifacts, or build, so existing outputs were not overwritten. The import-time make_paths expression was omitted in this isolated audit harness to avoid directory creation. Streamlit UI, CLI entry points, EDA rendering, and notebook execution: **not executed**.

The schemas below come from executing the functions in build.py and recommend.py, after reading their definitions; existing parquet files are not treated as schema authority. Function references include pandas callbacks and Streamlit callbacks, not just direct calls.

## Function map

| Function | Consumers | Status |
|---|---|---|
| app/dashboard.py::load_data (L86) | app/dashboard.py::main (L1031) | Referenced |
| app/dashboard.py::style (L100) | app/dashboard.py::main (L1031) | Referenced |
| app/dashboard.py::_esc (L329) | app/dashboard.py::info_card (L340) | Referenced |
| app/dashboard.py::metric (L334) | app/dashboard.py::section_overview (L396) | Referenced |
| app/dashboard.py::info_card (L340) | app/dashboard.py::section_artists (L507); app/dashboard.py::section_daily (L595); app/dashboard.py::section_heatmap (L682) | Referenced |
| app/dashboard.py::pink_divider (L351) | app/dashboard.py::main (L1031) | Referenced |
| app/dashboard.py::style_axes (L355) | app/dashboard.py::section_daily (L595); app/dashboard.py::section_heatmap (L682) | Referenced |
| app/dashboard.py::hero (L378) | app/dashboard.py::main (L1031) | Referenced |
| app/dashboard.py::section_overview (L396) | app/dashboard.py::main (L1031) | Referenced |
| app/dashboard.py::section_genres (L461) | app/dashboard.py::main (L1031) | Referenced |
| app/dashboard.py::section_artists (L507) | app/dashboard.py::main (L1031) | Referenced |
| app/dashboard.py::_artist_detail (L537) | app/dashboard.py::section_artists (L507) | Referenced |
| app/dashboard.py::section_repeat (L563) | app/dashboard.py::main (L1031) | Referenced |
| app/dashboard.py::section_daily (L595) | app/dashboard.py::main (L1031) | Referenced |
| app/dashboard.py::build_heatmap_table (L629) | app/dashboard.py::section_overview (L396); app/dashboard.py::section_heatmap (L682) | Referenced |
| app/dashboard.py::section_heatmap (L682) | app/dashboard.py::main (L1031) | Referenced |
| app/dashboard.py::_norm_text (L737) | app/dashboard.py::_genre_parts (L743); app/dashboard.py::fuzzy_genre_fallback (L840); app/dashboard.py::recommend_tracks (L859); app/dashboard.py::text_boost (L885) | Referenced |
| app/dashboard.py::_genre_parts (L743) | app/dashboard.py::_match_genres (L749) | Referenced |
| app/dashboard.py::_match_genres (L749) | app/dashboard.py::score_genre_affinity (L824) | Referenced |
| app/dashboard.py::load_mood_lexicon (L761) | app/dashboard.py::recommend_tracks (L859) | Referenced |
| app/dashboard.py::score_genre_affinity (L824) | app/dashboard.py::recommend_tracks (L859) | Referenced |
| app/dashboard.py::fuzzy_genre_fallback (L840) | app/dashboard.py::recommend_tracks (L859) | Referenced |
| app/dashboard.py::recommend_tracks (L859) | app/dashboard.py::section_recommend (L935) | Referenced |
| app/dashboard.py::_toggle_selection (L920) | app/dashboard.py::section_recommend (L935) | Referenced |
| app/dashboard.py::_clear_selection (L928) | app/dashboard.py::section_recommend (L935) | Referenced |
| app/dashboard.py::section_recommend (L935) | app/dashboard.py::main (L1031) | Referenced |
| app/dashboard.py::main (L1031) | app/dashboard.py::<module> | Referenced |
| app/dashboard.py::text_boost (L885) | app/dashboard.py::recommend_tracks (L859) | Referenced |
| scripts/make_recommendations.py::main (L8) | scripts/make_recommendations.py::<module> | Referenced |
| scripts/show_recommendations.py::main (L9) | scripts/show_recommendations.py::<module> | Referenced |
| src/music_analytics/build.py::get_col (L10) | src/music_analytics/build.py::load_library (L127); src/music_analytics/build.py::load_playlists (L163); src/music_analytics/build.py::make_daily (L185); src/music_analytics/build.py::make_plays (L252) | Referenced |
| src/music_analytics/build.py::id_text (L20) | src/music_analytics/build.py::load_library (L127); src/music_analytics/build.py::load_playlists (L163); src/music_analytics/build.py::make_daily (L185) | Referenced |
| src/music_analytics/build.py::key_text (L25) | src/music_analytics/build.py::load_library (L127); src/music_analytics/build.py::make_daily (L185); src/music_analytics/build.py::make_plays (L252) | Referenced |
| src/music_analytics/build.py::scale_score (L29) | src/music_analytics/build.py::make_features (L710) | Referenced |
| src/music_analytics/build.py::clean_source (L38) | src/music_analytics/build.py::source_label (L45) | Referenced |
| src/music_analytics/build.py::source_label (L45) | src/music_analytics/build.py::make_plays (L252) | Referenced |
| src/music_analytics/build.py::source_role (L84) | src/music_analytics/build.py::make_plays (L252) | Referenced |
| src/music_analytics/build.py::time_label (L100) | src/music_analytics/build.py::make_plays (L252); src/music_analytics/build.py::make_sessions (L661) | Referenced |
| src/music_analytics/build.py::top_value (L118) | src/music_analytics/build.py::make_tracks (L468); src/music_analytics/build.py::make_artists (L522); src/music_analytics/build.py::make_genres (L570); src/music_analytics/build.py::make_days (L593); src/music_analytics/build.py::make_sessions (L661) | Referenced |
| src/music_analytics/build.py::load_library (L127) | src/music_analytics/build.py::save_data (L903) | Referenced |
| src/music_analytics/build.py::load_playlists (L163) | src/music_analytics/build.py::save_data (L903) | Referenced |
| src/music_analytics/build.py::make_daily (L185) | src/music_analytics/build.py::save_data (L903) | Referenced |
| src/music_analytics/build.py::make_plays (L252) | src/music_analytics/build.py::save_data (L903) | Referenced |
| src/music_analytics/build.py::make_tracks (L468) | src/music_analytics/build.py::save_data (L903) | Referenced |
| src/music_analytics/build.py::make_artists (L522) | src/music_analytics/build.py::save_data (L903) | Referenced |
| src/music_analytics/build.py::make_albums (L549) | src/music_analytics/build.py::save_data (L903) | Referenced |
| src/music_analytics/build.py::make_genres (L570) | src/music_analytics/build.py::save_data (L903) | Referenced |
| src/music_analytics/build.py::make_days (L593) | src/music_analytics/build.py::save_data (L903) | Referenced |
| src/music_analytics/build.py::make_hours (L617) | src/music_analytics/build.py::save_data (L903) | Referenced |
| src/music_analytics/build.py::make_sources (L635) | src/music_analytics/build.py::save_data (L903) | Referenced |
| src/music_analytics/build.py::make_sessions (L661) | src/music_analytics/build.py::save_data (L903) | Referenced |
| src/music_analytics/build.py::make_features (L710) | src/music_analytics/build.py::save_data (L903) | Referenced |
| src/music_analytics/build.py::make_life (L789) | src/music_analytics/build.py::save_data (L903) | Referenced |
| src/music_analytics/build.py::make_profile (L833) | src/music_analytics/build.py::save_data (L903) | Referenced |
| src/music_analytics/build.py::save_check (L882) | src/music_analytics/build.py::save_data (L903) | Referenced |
| src/music_analytics/build.py::save_data (L903) | scripts/make_data.py::<module> | Referenced |
| src/music_analytics/paths.py::make_paths (L18) | src/music_analytics/paths.py::<module> | Referenced |
| src/music_analytics/read.py::clean_name (L12) | src/music_analytics/read.py::clean_cols (L20); src/music_analytics/read.py::audit_data (L98) | Referenced |
| src/music_analytics/read.py::clean_cols (L20) | src/music_analytics/read.py::read_csv (L53); src/music_analytics/read.py::read_zip (L61) | Referenced |
| src/music_analytics/read.py::text_key (L26) | src/music_analytics/build.py::key_text (L25) | Referenced |
| src/music_analytics/read.py::find_file (L35) | src/music_analytics/read.py::need_file (L44) | Referenced |
| src/music_analytics/read.py::need_file (L44) | src/music_analytics/read.py::read_csv (L53); src/music_analytics/read.py::read_zip (L61) | Referenced |
| src/music_analytics/read.py::read_csv (L53) | src/music_analytics/build.py::make_daily (L185); src/music_analytics/build.py::make_plays (L252) | Referenced |
| src/music_analytics/read.py::read_zip (L61) | src/music_analytics/build.py::load_library (L127); src/music_analytics/build.py::load_playlists (L163) | Referenced |
| src/music_analytics/read.py::raw_files (L85) | src/music_analytics/read.py::audit_data (L98) | Referenced |
| src/music_analytics/read.py::audit_data (L98) | scripts/audit_data.py::<module>; src/music_analytics/build.py::save_data (L903) | Referenced |
| src/music_analytics/read.py::as_time (L147) | src/music_analytics/build.py::load_library (L127); src/music_analytics/build.py::load_playlists (L163); src/music_analytics/build.py::make_plays (L252) | Referenced |
| src/music_analytics/read.py::as_day (L156) | src/music_analytics/build.py::make_daily (L185) | Referenced |
| src/music_analytics/read.py::split_track (L161) | src/music_analytics/build.py::make_daily (L185) | Referenced |
| src/music_analytics/read.py::safe_rate (L180) | src/music_analytics/build.py::make_daily (L185); src/music_analytics/build.py::make_plays (L252); src/music_analytics/build.py::make_tracks (L468); src/music_analytics/build.py::make_artists (L522); src/music_analytics/build.py::make_albums (L549); src/music_analytics/build.py::make_genres (L570); src/music_analytics/build.py::make_days (L593); src/music_analytics/build.py::make_hours (L617); src/music_analytics/build.py::make_sources (L635); src/music_analytics/build.py::make_sessions (L661) | Referenced |
| src/music_analytics/recommend.py::need_col (L16) | src/music_analytics/recommend.py::prepare (L116) | Referenced |
| src/music_analytics/recommend.py::safe_num (L22) | src/music_analytics/recommend.py::prepare (L116) | Referenced |
| src/music_analytics/recommend.py::safe_text (L29) | src/music_analytics/recommend.py::fill_text (L35); src/music_analytics/recommend.py::make_text (L93); src/music_analytics/recommend.py::prepare (L116) | Referenced |
| src/music_analytics/recommend.py::fill_text (L35) | src/music_analytics/recommend.py::prepare (L116) | Referenced |
| src/music_analytics/recommend.py::clean_text (L46) | src/music_analytics/recommend.py::fill_text (L35); src/music_analytics/recommend.py::make_text (L93); src/music_analytics/recommend.py::find_track (L531) | Referenced |
| src/music_analytics/recommend.py::role_name (L54) | src/music_analytics/recommend.py::prepare (L116) | Referenced |
| src/music_analytics/recommend.py::role_reason (L67) | src/music_analytics/recommend.py::prepare (L116) | Referenced |
| src/music_analytics/recommend.py::make_text (L93) | src/music_analytics/recommend.py::prepare (L116) | Referenced |
| src/music_analytics/recommend.py::prepare (L116) | src/music_analytics/recommend.py::build (L479) | Referenced |
| src/music_analytics/recommend.py::encoder (L194) | src/music_analytics/recommend.py::make_matrix (L201) | Referenced |
| src/music_analytics/recommend.py::make_matrix (L201) | src/music_analytics/recommend.py::build (L479) | Referenced |
| src/music_analytics/recommend.py::make_model (L274) | src/music_analytics/recommend.py::build (L479) | Referenced |
| src/music_analytics/recommend.py::make_candidates (L288) | src/music_analytics/recommend.py::build (L479) | Referenced |
| src/music_analytics/recommend.py::make_pairs (L320) | src/music_analytics/recommend.py::build (L479) | Referenced |
| src/music_analytics/recommend.py::make_profile (L378) | src/music_analytics/recommend.py::build (L479) | Referenced |
| src/music_analytics/recommend.py::sample_scores (L433) | src/music_analytics/recommend.py::build (L479) | Referenced |
| src/music_analytics/recommend.py::save_artifacts (L458) | src/music_analytics/recommend.py::build (L479) | Referenced |
| src/music_analytics/recommend.py::build (L479) | scripts/make_recommendations.py::main (L8) | Referenced |
| src/music_analytics/recommend.py::load_outputs (L515) | src/music_analytics/recommend.py::find_track (L531); src/music_analytics/recommend.py::recommend_for (L550) | Referenced |
| src/music_analytics/recommend.py::find_track (L531) | scripts/show_recommendations.py::main (L9) | Referenced |
| src/music_analytics/recommend.py::recommend_for (L550) | scripts/show_recommendations.py::main (L9) | Referenced |

The two make_profile functions are in separate modules; they do not shadow each other in the existing import graph. hero is called, but its data parameter is unused. All functions in the ten source files have a call or callback consumer; deletion of whole chains depends on retiring their output or CLI consumer.

## Processed tables

All 20 current output schemas are listed, including the four recommendation outputs. A writer is not counted as a downstream consumer. In-memory pipeline consumers and persisted-file consumers are separated.

| Table | Producer | In-memory / application consumer | Notebook consumer | Rows |
|---|---|---|---|---|
| library.parquet | load_library | build.make_daily, make_plays, make_tracks | cells 9, 23, 26 (date conversion / schema QA) | 10,633 |
| playlists.parquet | load_playlists | No post-build analytical consumer | cells 9, 26 (schema QA only) | 144 |
| playlist_tracks.parquet | load_playlists | build.make_tracks (playlist counts) | cells 9, 26 (schema QA only) | 16,687 |
| daily_tracks.parquet | make_daily | build.make_plays (metadata fallback) | cells 9, 23, 24 (load/date conversion/registry only) | 5,042 |
| plays.parquet | make_plays | build.make_tracks, make_artists, make_albums, make_genres, make_days, make_hours, make_sources, make_sessions, make_features, make_profile, save_check; dashboard.load_data and sections; make_eda module | cells 9, 23, 26, 31–51 | 10,454 |
| tracks.parquet | make_tracks | build.make_features, make_profile, save_check; dashboard.load_data, section_overview, section_artists, _artist_detail, section_repeat, section_recommend/recommend_tracks; make_eda module | Not directly loaded; all columns propagate to features | 2,962 |
| artists.parquet | make_artists | build.make_profile, save_check; dashboard.load_data, section_overview, section_artists; make_eda module | cells 9, 23, 26, 40, 52 | 995 |
| albums.parquet | make_albums | build.save_check (row count) | cells 9, 23, 26 (date conversion / schema QA) | 1,853 |
| genres.parquet | make_genres | build.save_check; dashboard.load_data, section_overview, section_genres, section_recommend; make_eda module | cells 9, 26, 40, 54 | 70 |
| days.parquet | make_days | dashboard.load_data, section_overview, section_daily; make_eda module | cells 9, 23, 26, 49 | 143 |
| hours.parquet | make_hours | dashboard.load_data; unreachable schema-incompatible heatmap fallback; make_eda existence check only | cells 9, 26, 50 (hourly heatmap) | 155 |
| sources.parquet | make_sources | build.make_profile; make_eda existence check only | cells 9, 26, 40, 56 | 10 |
| sessions.parquet | make_sessions | build.save_check (row count); make_eda existence check only | cells 9, 23, 26, 40, 58 | 448 |
| features.parquet | make_features | build.make_life, save_check; recommend.build -> prepare; make_eda readiness count; dashboard.load_data loads but does not consume | cells 9, 23, 26, 35, 39, 62, 64, 66 | 2,962 |
| life.parquet | make_life | No application read | cells 9, 23, 26, 60 (lifecycle analysis) | 2,962 |
| profile.parquet | make_profile | build.save_check; make_eda profile_type | cells 9, 48 (all metrics displayed) | 12 |
| recommend_candidates.parquet | recommend.make_candidates | recommend.load_outputs -> find_track -> show_recommendations.main | cells 9, 26, 35, 69 | 2,962 |
| recommendations.parquet | recommend.make_pairs | recommend.load_outputs -> recommend_for -> show_recommendations.main | cells 9, 26, 35, 70, 72 | 17,972 |
| recommend_profile.parquet | recommend.make_profile | recommend.load_outputs loads only; make_recommendations prints path | cells 9, 68 (all metrics displayed) | 8 |
| recommend_sample.parquet | recommend.sample_scores | recommend.load_outputs loads only | cells 9, 24 (load/registry only; ZERO analytical consumers) | 132 |

## Every written column

Each column has a row below. Named-reference locations are filtered to downstream consumers of each table (including propagated feature copies). They identify matching column literals/row attributes within those consumers. A scope that reads several tables can still use the same column name for more than one table, so this conservative static evidence is not sufficient by itself to approve deletion. Producer-only writes and unrelated scopes are excluded. Generic whole-table QA/display is listed separately and really does consume all columns, even without naming each one. No column is approved for deletion based solely on absence from this index.

| Table | Written column | Named-reference evidence (file/function or cell) | Whole-table consumer / zero status |
|---|---|---|---|
| library | track_id | src/music_analytics/build.py::make_daily (L185); src/music_analytics/build.py::make_plays (L252); src/music_analytics/build.py::make_tracks (L468) | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| library | apple_id | src/music_analytics/build.py::make_daily (L185); src/music_analytics/build.py::make_plays (L252); src/music_analytics/build.py::make_tracks (L468) | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| library | track | src/music_analytics/build.py::make_daily (L185); src/music_analytics/build.py::make_plays (L252); src/music_analytics/build.py::make_tracks (L468) | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| library | artist | src/music_analytics/build.py::make_daily (L185); src/music_analytics/build.py::make_plays (L252); src/music_analytics/build.py::make_tracks (L468) | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| library | album | src/music_analytics/build.py::make_daily (L185); src/music_analytics/build.py::make_plays (L252); src/music_analytics/build.py::make_tracks (L468) | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| library | genre | src/music_analytics/build.py::make_daily (L185); src/music_analytics/build.py::make_plays (L252); src/music_analytics/build.py::make_tracks (L468) | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| library | duration_milliseconds | src/music_analytics/build.py::make_daily (L185); src/music_analytics/build.py::make_plays (L252); src/music_analytics/build.py::make_tracks (L468) | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| library | library_plays | src/music_analytics/build.py::make_plays (L252); src/music_analytics/build.py::make_tracks (L468) | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| library | library_skips | src/music_analytics/build.py::make_tracks (L468) | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| library | added_at | src/music_analytics/build.py::make_tracks (L468); notebooks/01_exploratory_data_analysis.ipynb::cell 23 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| library | release_at | src/music_analytics/build.py::make_tracks (L468); notebooks/01_exploratory_data_analysis.ipynb::cell 23 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| library | track_name | src/music_analytics/build.py::make_daily (L185); src/music_analytics/build.py::make_plays (L252) | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| library | artist_name | src/music_analytics/build.py::make_daily (L185); src/music_analytics/build.py::make_plays (L252) | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| library | album_name | src/music_analytics/build.py::make_daily (L185); src/music_analytics/build.py::make_plays (L252) | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| library | track_key | src/music_analytics/build.py::make_daily (L185); src/music_analytics/build.py::make_plays (L252); src/music_analytics/build.py::make_tracks (L468) | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| playlists | playlist_id | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| playlists | playlist | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| playlists | playlist_type | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| playlists | added_at | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| playlists | track_count | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| playlist_tracks | playlist_id | src/music_analytics/build.py::make_tracks (L468) | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| playlist_tracks | playlist | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| playlist_tracks | playlist_type | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| playlist_tracks | track_id | src/music_analytics/build.py::make_tracks (L468) | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| daily_tracks | apple_id | ZERO downstream column consumers (load/registry only) | Do not confuse temporary construction use with a consumer of the written column |
| daily_tracks | track | ZERO downstream column consumers (load/registry only) | Do not confuse temporary construction use with a consumer of the written column |
| daily_tracks | artist | src/music_analytics/build.py::make_plays (daily_title selection/sort) | Consumed as listed |
| daily_tracks | date | notebooks/01_exploratory_data_analysis.ipynb::cell 23 -> set_time (date conversion only) | Consumed as listed |
| daily_tracks | hour | ZERO downstream column consumers (load/registry only) | Do not confuse temporary construction use with a consumer of the written column |
| daily_tracks | played_at | notebooks/01_exploratory_data_analysis.ipynb::cell 23 -> set_time (date conversion only) | Consumed as listed |
| daily_tracks | play_milliseconds | ZERO downstream column consumers (load/registry only) | Do not confuse temporary construction use with a consumer of the written column |
| daily_tracks | plays | src/music_analytics/build.py::make_plays (daily_title selection/sort) | Consumed as listed |
| daily_tracks | skips | ZERO downstream column consumers (load/registry only) | Do not confuse temporary construction use with a consumer of the written column |
| daily_tracks | source_type | ZERO downstream column consumers (load/registry only) | Do not confuse temporary construction use with a consumer of the written column |
| daily_tracks | end_reason | ZERO downstream column consumers (load/registry only) | Do not confuse temporary construction use with a consumer of the written column |
| daily_tracks | ignore_recs | ZERO downstream column consumers (load/registry only) | Do not confuse temporary construction use with a consumer of the written column |
| daily_tracks | track_id | ZERO downstream column consumers (load/registry only) | Do not confuse temporary construction use with a consumer of the written column |
| daily_tracks | track_key | src/music_analytics/build.py::make_plays (daily_title selection/sort) | Consumed as listed |
| daily_tracks | album | src/music_analytics/build.py::make_plays (daily_title selection/sort) | Consumed as listed |
| daily_tracks | genre | src/music_analytics/build.py::make_plays (daily_title selection/sort) | Consumed as listed |
| daily_tracks | duration_milliseconds | src/music_analytics/build.py::make_plays (daily_title selection/sort) | Consumed as listed |
| daily_tracks | track_name | src/music_analytics/build.py::make_plays (daily_title selection/sort) | Consumed as listed |
| daily_tracks | artist_name | ZERO downstream column consumers (load/registry only) | Do not confuse temporary construction use with a consumer of the written column |
| daily_tracks | album_name | ZERO downstream column consumers (load/registry only) | Do not confuse temporary construction use with a consumer of the written column |
| daily_tracks | minutes | src/music_analytics/build.py::make_plays (daily_title selection/sort) | Consumed as listed |
| daily_tracks | skip_rate | ZERO downstream column consumers (load/registry only) | Do not confuse temporary construction use with a consumer of the written column |
| plays | event_id | notebooks/01_exploratory_data_analysis.ipynb::cell 51 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| plays | played_at | app/dashboard.py::build_heatmap_table (L629); src/music_analytics/build.py::make_tracks (L468); src/music_analytics/build.py::make_artists (L522); src/music_analytics/build.py::make_albums (L549); src/music_analytics/build.py::make_sessions (L661); src/music_analytics/build.py::make_features (L710); src/music_analytics/build.py::save_check (L882); notebooks/01_exploratory_data_analysis.ipynb::cell 23; notebooks/01_exploratory_data_analysis.ipynb::cell 31; notebooks/01_exploratory_data_analysis.ipynb::cell 39 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| plays | start_at | notebooks/01_exploratory_data_analysis.ipynb::cell 23 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| plays | received_at | notebooks/01_exploratory_data_analysis.ipynb::cell 23 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| plays | date | app/dashboard.py::section_overview (L396); scripts/make_eda.py::<module>; src/music_analytics/build.py::make_tracks (L468); src/music_analytics/build.py::make_artists (L522); src/music_analytics/build.py::make_days (L593); notebooks/01_exploratory_data_analysis.ipynb::cell 23; notebooks/01_exploratory_data_analysis.ipynb::cell 33; notebooks/01_exploratory_data_analysis.ipynb::cell 37; notebooks/01_exploratory_data_analysis.ipynb::cell 39 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| plays | month | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| plays | weekday | app/dashboard.py::section_overview (L396); app/dashboard.py::build_heatmap_table (L629); src/music_analytics/build.py::make_hours (L617) | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| plays | weekday_num | src/music_analytics/build.py::make_hours (L617) | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| plays | hour | app/dashboard.py::build_heatmap_table (L629); src/music_analytics/build.py::make_hours (L617); src/music_analytics/build.py::make_sessions (L661) | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| plays | time_block | src/music_analytics/build.py::make_genres (L570); src/music_analytics/build.py::make_sessions (L661); src/music_analytics/build.py::make_profile (L833); notebooks/01_exploratory_data_analysis.ipynb::cell 40; notebooks/01_exploratory_data_analysis.ipynb::cell 51 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| plays | track_key | src/music_analytics/build.py::make_tracks (L468); src/music_analytics/build.py::make_artists (L522); src/music_analytics/build.py::make_albums (L549); src/music_analytics/build.py::make_genres (L570); src/music_analytics/build.py::make_days (L593); src/music_analytics/build.py::make_hours (L617); src/music_analytics/build.py::make_sources (L635); src/music_analytics/build.py::make_sessions (L661); src/music_analytics/build.py::make_profile (L833); notebooks/01_exploratory_data_analysis.ipynb::cell 33; notebooks/01_exploratory_data_analysis.ipynb::cell 37; notebooks/01_exploratory_data_analysis.ipynb::cell 39 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| plays | track_id | src/music_analytics/build.py::make_tracks (L468) | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| plays | apple_id | src/music_analytics/build.py::make_tracks (L468) | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| plays | track | app/dashboard.py::section_overview (L396); app/dashboard.py::_artist_detail (L537); app/dashboard.py::section_repeat (L563); app/dashboard.py::build_heatmap_table (L629); src/music_analytics/build.py::make_tracks (L468); src/music_analytics/build.py::make_features (L710) | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| plays | artist | app/dashboard.py::section_overview (L396); app/dashboard.py::section_artists (L507); app/dashboard.py::_artist_detail (L537); app/dashboard.py::section_repeat (L563); app/dashboard.py::build_heatmap_table (L629); src/music_analytics/build.py::make_tracks (L468); src/music_analytics/build.py::make_artists (L522); src/music_analytics/build.py::make_albums (L549); src/music_analytics/build.py::make_genres (L570); src/music_analytics/build.py::make_days (L593); src/music_analytics/build.py::make_sources (L635); src/music_analytics/build.py::make_sessions (L661); src/music_analytics/build.py::make_features (L710); notebooks/01_exploratory_data_analysis.ipynb::cell 33; notebooks/01_exploratory_data_analysis.ipynb::cell 37; notebooks/01_exploratory_data_analysis.ipynb::cell 39; notebooks/01_exploratory_data_analysis.ipynb::cell 40 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| plays | album | src/music_analytics/build.py::make_tracks (L468); src/music_analytics/build.py::make_artists (L522); src/music_analytics/build.py::make_albums (L549); src/music_analytics/build.py::make_features (L710); notebooks/01_exploratory_data_analysis.ipynb::cell 33; notebooks/01_exploratory_data_analysis.ipynb::cell 39 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| plays | genre | app/dashboard.py::section_overview (L396); app/dashboard.py::section_genres (L461); scripts/make_eda.py::<module>; src/music_analytics/build.py::make_tracks (L468); src/music_analytics/build.py::make_artists (L522); src/music_analytics/build.py::make_genres (L570); src/music_analytics/build.py::make_days (L593); src/music_analytics/build.py::make_sources (L635); src/music_analytics/build.py::make_sessions (L661); src/music_analytics/build.py::make_features (L710); src/music_analytics/build.py::make_profile (L833); notebooks/01_exploratory_data_analysis.ipynb::cell 33; notebooks/01_exploratory_data_analysis.ipynb::cell 39; notebooks/01_exploratory_data_analysis.ipynb::cell 40 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| plays | display | src/music_analytics/build.py::make_tracks (L468) | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| plays | play_milliseconds | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| plays | duration_milliseconds | src/music_analytics/build.py::make_tracks (L468) | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| plays | minutes | app/dashboard.py::section_overview (L396); app/dashboard.py::_artist_detail (L537); app/dashboard.py::build_heatmap_table (L629); scripts/make_eda.py::<module>; src/music_analytics/build.py::make_tracks (L468); src/music_analytics/build.py::make_artists (L522); src/music_analytics/build.py::make_albums (L549); src/music_analytics/build.py::make_genres (L570); src/music_analytics/build.py::make_days (L593); src/music_analytics/build.py::make_hours (L617); src/music_analytics/build.py::make_sources (L635); src/music_analytics/build.py::make_sessions (L661); src/music_analytics/build.py::make_features (L710); src/music_analytics/build.py::save_check (L882); notebooks/01_exploratory_data_analysis.ipynb::cell 39; notebooks/01_exploratory_data_analysis.ipynb::cell 51 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| plays | play_share | src/music_analytics/build.py::make_tracks (L468); src/music_analytics/build.py::make_sources (L635) | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| plays | good_play | src/music_analytics/build.py::make_tracks (L468); src/music_analytics/build.py::make_artists (L522) | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| plays | full_play | src/music_analytics/build.py::make_tracks (L468); src/music_analytics/build.py::make_artists (L522); src/music_analytics/build.py::make_albums (L549); src/music_analytics/build.py::make_genres (L570); src/music_analytics/build.py::make_days (L593); src/music_analytics/build.py::make_hours (L617); src/music_analytics/build.py::make_sources (L635); src/music_analytics/build.py::make_sessions (L661); src/music_analytics/build.py::make_profile (L833); notebooks/01_exploratory_data_analysis.ipynb::cell 39; notebooks/01_exploratory_data_analysis.ipynb::cell 51 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| plays | friction | src/music_analytics/build.py::make_tracks (L468); src/music_analytics/build.py::make_artists (L522); src/music_analytics/build.py::make_albums (L549); src/music_analytics/build.py::make_genres (L570); src/music_analytics/build.py::make_days (L593); src/music_analytics/build.py::make_hours (L617); src/music_analytics/build.py::make_sources (L635); src/music_analytics/build.py::make_sessions (L661); src/music_analytics/build.py::make_profile (L833); notebooks/01_exploratory_data_analysis.ipynb::cell 39; notebooks/01_exploratory_data_analysis.ipynb::cell 51 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| plays | end_reason | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| plays | source_type | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| plays | source_label | src/music_analytics/build.py::make_tracks (L468); src/music_analytics/build.py::make_artists (L522); src/music_analytics/build.py::make_genres (L570); src/music_analytics/build.py::make_days (L593); src/music_analytics/build.py::make_sources (L635); src/music_analytics/build.py::make_sessions (L661); src/music_analytics/build.py::make_profile (L833); notebooks/01_exploratory_data_analysis.ipynb::cell 40 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| plays | source_role | src/music_analytics/build.py::make_tracks (L468); src/music_analytics/build.py::make_sources (L635); src/music_analytics/build.py::make_profile (L833) | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| plays | feature | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| plays | container | app/dashboard.py::section_genres (L461); app/dashboard.py::section_repeat (L563) | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| plays | container_type | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| plays | device | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| plays | media_type | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| plays | auto_play | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| plays | shuffle_play | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| plays | repeat_play | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| plays | use_history | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| plays | offline | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| plays | play_num | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| plays | first_play | src/music_analytics/build.py::make_sources (L635); src/music_analytics/build.py::make_profile (L833); src/music_analytics/build.py::save_check (L882); notebooks/01_exploratory_data_analysis.ipynb::cell 23; notebooks/01_exploratory_data_analysis.ipynb::cell 39 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| plays | repeat_seen | src/music_analytics/build.py::make_sources (L635); notebooks/01_exploratory_data_analysis.ipynb::cell 39 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| tracks | track_key | src/music_analytics/build.py::make_profile (L833) | build.make_features copies all columns -> EDA notebook cell 26 QA |
| tracks | track | app/dashboard.py::section_overview (L396); app/dashboard.py::_artist_detail (L537); app/dashboard.py::section_repeat (L563); app/dashboard.py::recommend_tracks (L859); app/dashboard.py::section_recommend (L935); app/dashboard.py::text_boost (L885); src/music_analytics/build.py::make_features (L710) | build.make_features copies all columns -> EDA notebook cell 26 QA |
| tracks | artist | app/dashboard.py::section_overview (L396); app/dashboard.py::_artist_detail (L537); app/dashboard.py::section_repeat (L563); app/dashboard.py::recommend_tracks (L859); app/dashboard.py::section_recommend (L935); app/dashboard.py::text_boost (L885); src/music_analytics/build.py::make_features (L710) | build.make_features copies all columns -> EDA notebook cell 26 QA |
| tracks | album | src/music_analytics/build.py::make_features (L710) | build.make_features copies all columns -> EDA notebook cell 26 QA |
| tracks | genre | app/dashboard.py::section_overview (L396); app/dashboard.py::fuzzy_genre_fallback (L840); app/dashboard.py::recommend_tracks (L859); app/dashboard.py::section_recommend (L935); scripts/make_eda.py::<module>; src/music_analytics/build.py::make_features (L710); src/music_analytics/build.py::make_profile (L833) | build.make_features copies all columns -> EDA notebook cell 26 QA |
| tracks | display | ZERO named downstream references found | build.make_features copies all columns -> EDA notebook cell 26 QA |
| tracks | plays | app/dashboard.py::section_overview (L396); app/dashboard.py::_artist_detail (L537); app/dashboard.py::section_repeat (L563); app/dashboard.py::recommend_tracks (L859); scripts/make_eda.py::<module>; src/music_analytics/build.py::make_features (L710); src/music_analytics/build.py::make_profile (L833) | build.make_features copies all columns -> EDA notebook cell 26 QA |
| tracks | minutes | app/dashboard.py::section_overview (L396); app/dashboard.py::_artist_detail (L537); scripts/make_eda.py::<module>; src/music_analytics/build.py::make_features (L710) | build.make_features copies all columns -> EDA notebook cell 26 QA |
| tracks | good_plays | ZERO named downstream references found | build.make_features copies all columns -> EDA notebook cell 26 QA |
| tracks | full_plays | ZERO named downstream references found | build.make_features copies all columns -> EDA notebook cell 26 QA |
| tracks | friction_plays | ZERO named downstream references found | build.make_features copies all columns -> EDA notebook cell 26 QA |
| tracks | average_share | ZERO named downstream references found | build.make_features copies all columns -> EDA notebook cell 26 QA |
| tracks | first_play | src/music_analytics/build.py::make_profile (L833) | build.make_features copies all columns -> EDA notebook cell 26 QA |
| tracks | last_play | src/music_analytics/build.py::make_features (L710) | build.make_features copies all columns -> EDA notebook cell 26 QA |
| tracks | active_days | src/music_analytics/build.py::make_features (L710) | build.make_features copies all columns -> EDA notebook cell 26 QA |
| tracks | source_count | ZERO named downstream references found | build.make_features copies all columns -> EDA notebook cell 26 QA |
| tracks | source_top | ZERO named downstream references found | build.make_features copies all columns -> EDA notebook cell 26 QA |
| tracks | role_top | ZERO named downstream references found | build.make_features copies all columns -> EDA notebook cell 26 QA |
| tracks | track_id | ZERO named downstream references found | build.make_features copies all columns -> EDA notebook cell 26 QA |
| tracks | apple_id | ZERO named downstream references found | build.make_features copies all columns -> EDA notebook cell 26 QA |
| tracks | duration_milliseconds | ZERO named downstream references found | build.make_features copies all columns -> EDA notebook cell 26 QA |
| tracks | library_plays | ZERO named downstream references found | build.make_features copies all columns -> EDA notebook cell 26 QA |
| tracks | library_skips | ZERO named downstream references found | build.make_features copies all columns -> EDA notebook cell 26 QA |
| tracks | added_at | ZERO named downstream references found | build.make_features copies all columns -> EDA notebook cell 26 QA |
| tracks | release_at | ZERO named downstream references found | build.make_features copies all columns -> EDA notebook cell 26 QA |
| tracks | playlist_count | src/music_analytics/build.py::make_features (L710) | build.make_features copies all columns -> EDA notebook cell 26 QA |
| tracks | good_rate | ZERO named downstream references found | build.make_features copies all columns -> EDA notebook cell 26 QA |
| tracks | full_rate | app/dashboard.py::recommend_tracks (L859); scripts/make_eda.py::<module>; src/music_analytics/build.py::make_features (L710) | build.make_features copies all columns -> EDA notebook cell 26 QA |
| tracks | friction_rate | app/dashboard.py::recommend_tracks (L859); src/music_analytics/build.py::make_features (L710) | build.make_features copies all columns -> EDA notebook cell 26 QA |
| tracks | library_ready | ZERO named downstream references found | build.make_features copies all columns -> EDA notebook cell 26 QA |
| tracks | retained | src/music_analytics/build.py::make_profile (L833) | build.make_features copies all columns -> EDA notebook cell 26 QA |
| tracks | recommender_ready | scripts/make_eda.py::<module> | build.make_features copies all columns -> EDA notebook cell 26 QA |
| artists | artist | app/dashboard.py::section_overview (L396); app/dashboard.py::section_artists (L507); notebooks/01_exploratory_data_analysis.ipynb::cell 40; notebooks/01_exploratory_data_analysis.ipynb::cell 52 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| artists | plays | app/dashboard.py::section_overview (L396); app/dashboard.py::section_artists (L507); src/music_analytics/build.py::make_profile (L833); notebooks/01_exploratory_data_analysis.ipynb::cell 40; notebooks/01_exploratory_data_analysis.ipynb::cell 52 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| artists | tracks | app/dashboard.py::section_overview (L396); app/dashboard.py::section_artists (L507); notebooks/01_exploratory_data_analysis.ipynb::cell 52 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| artists | albums | notebooks/01_exploratory_data_analysis.ipynb::cell 52 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| artists | genres | app/dashboard.py::section_overview (L396); notebooks/01_exploratory_data_analysis.ipynb::cell 52 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| artists | minutes | app/dashboard.py::section_overview (L396); notebooks/01_exploratory_data_analysis.ipynb::cell 52 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| artists | good_plays | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| artists | full_plays | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| artists | friction_plays | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| artists | first_play | src/music_analytics/build.py::make_profile (L833); notebooks/01_exploratory_data_analysis.ipynb::cell 23 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| artists | last_play | notebooks/01_exploratory_data_analysis.ipynb::cell 23 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| artists | active_days | notebooks/01_exploratory_data_analysis.ipynb::cell 52 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| artists | source_top | notebooks/01_exploratory_data_analysis.ipynb::cell 52 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| artists | good_rate | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| artists | full_rate | notebooks/01_exploratory_data_analysis.ipynb::cell 52 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| artists | friction_rate | notebooks/01_exploratory_data_analysis.ipynb::cell 52 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| albums | album | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| albums | artist | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| albums | plays | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| albums | tracks | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| albums | minutes | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| albums | full_plays | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| albums | friction_plays | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| albums | first_play | notebooks/01_exploratory_data_analysis.ipynb::cell 23 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| albums | last_play | notebooks/01_exploratory_data_analysis.ipynb::cell 23 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| albums | full_rate | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| albums | friction_rate | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| genres | genre | app/dashboard.py::section_overview (L396); app/dashboard.py::section_genres (L461); app/dashboard.py::section_recommend (L935); scripts/make_eda.py::<module>; notebooks/01_exploratory_data_analysis.ipynb::cell 40; notebooks/01_exploratory_data_analysis.ipynb::cell 54 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| genres | plays | app/dashboard.py::section_overview (L396); app/dashboard.py::section_genres (L461); scripts/make_eda.py::<module>; notebooks/01_exploratory_data_analysis.ipynb::cell 40; notebooks/01_exploratory_data_analysis.ipynb::cell 54 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| genres | tracks | app/dashboard.py::section_overview (L396); app/dashboard.py::section_recommend (L935); notebooks/01_exploratory_data_analysis.ipynb::cell 54 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| genres | artists | app/dashboard.py::section_overview (L396); notebooks/01_exploratory_data_analysis.ipynb::cell 54 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| genres | minutes | app/dashboard.py::section_overview (L396); scripts/make_eda.py::<module>; notebooks/01_exploratory_data_analysis.ipynb::cell 54 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| genres | full_plays | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| genres | friction_plays | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| genres | source_top | notebooks/01_exploratory_data_analysis.ipynb::cell 54 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| genres | time_top | notebooks/01_exploratory_data_analysis.ipynb::cell 54 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| genres | full_rate | scripts/make_eda.py::<module>; notebooks/01_exploratory_data_analysis.ipynb::cell 54 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| genres | friction_rate | notebooks/01_exploratory_data_analysis.ipynb::cell 54 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| genres | share | notebooks/01_exploratory_data_analysis.ipynb::cell 54 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| days | date | app/dashboard.py::section_overview (L396); app/dashboard.py::section_daily (L595); scripts/make_eda.py::<module>; notebooks/01_exploratory_data_analysis.ipynb::cell 23; notebooks/01_exploratory_data_analysis.ipynb::cell 49 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| days | plays | app/dashboard.py::section_overview (L396); app/dashboard.py::section_daily (L595); scripts/make_eda.py::<module>; notebooks/01_exploratory_data_analysis.ipynb::cell 49 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| days | tracks | app/dashboard.py::section_overview (L396); app/dashboard.py::section_daily (L595); notebooks/01_exploratory_data_analysis.ipynb::cell 49 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| days | artists | app/dashboard.py::section_overview (L396); notebooks/01_exploratory_data_analysis.ipynb::cell 49 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| days | minutes | app/dashboard.py::section_overview (L396); app/dashboard.py::section_daily (L595); scripts/make_eda.py::<module>; notebooks/01_exploratory_data_analysis.ipynb::cell 49 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| days | full_plays | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| days | friction_plays | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| days | top_artist | app/dashboard.py::section_daily (L595); notebooks/01_exploratory_data_analysis.ipynb::cell 49 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| days | top_genre | app/dashboard.py::section_daily (L595); notebooks/01_exploratory_data_analysis.ipynb::cell 49 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| days | top_source | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| days | full_rate | scripts/make_eda.py::<module>; notebooks/01_exploratory_data_analysis.ipynb::cell 49 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| days | friction_rate | notebooks/01_exploratory_data_analysis.ipynb::cell 49 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| hours | weekday_num | notebooks/01_exploratory_data_analysis.ipynb::cell 50 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| hours | weekday | app/dashboard.py::build_heatmap_table (L629); notebooks/01_exploratory_data_analysis.ipynb::cell 50 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| hours | hour | app/dashboard.py::build_heatmap_table (L629); notebooks/01_exploratory_data_analysis.ipynb::cell 50 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| hours | plays | app/dashboard.py::build_heatmap_table (L629); notebooks/01_exploratory_data_analysis.ipynb::cell 50 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| hours | minutes | app/dashboard.py::build_heatmap_table (L629) | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| hours | full_plays | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| hours | friction_plays | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| hours | full_rate | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| hours | friction_rate | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| sources | source_label | src/music_analytics/build.py::make_profile (L833); notebooks/01_exploratory_data_analysis.ipynb::cell 40; notebooks/01_exploratory_data_analysis.ipynb::cell 56 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| sources | source_role | src/music_analytics/build.py::make_profile (L833); notebooks/01_exploratory_data_analysis.ipynb::cell 56 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| sources | plays | src/music_analytics/build.py::make_profile (L833); notebooks/01_exploratory_data_analysis.ipynb::cell 40; notebooks/01_exploratory_data_analysis.ipynb::cell 56 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| sources | tracks | notebooks/01_exploratory_data_analysis.ipynb::cell 56 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| sources | artists | notebooks/01_exploratory_data_analysis.ipynb::cell 56 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| sources | genres | notebooks/01_exploratory_data_analysis.ipynb::cell 56 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| sources | minutes | notebooks/01_exploratory_data_analysis.ipynb::cell 56 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| sources | first_plays | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| sources | repeat_plays | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| sources | full_plays | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| sources | friction_plays | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| sources | play_share | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| sources | discovery_share | src/music_analytics/build.py::make_profile (L833); notebooks/01_exploratory_data_analysis.ipynb::cell 56 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| sources | repeat_share | notebooks/01_exploratory_data_analysis.ipynb::cell 56 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| sources | full_rate | notebooks/01_exploratory_data_analysis.ipynb::cell 56 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| sources | friction_rate | notebooks/01_exploratory_data_analysis.ipynb::cell 56 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| sessions | session | notebooks/01_exploratory_data_analysis.ipynb::cell 58 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| sessions | start | notebooks/01_exploratory_data_analysis.ipynb::cell 23 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| sessions | end | notebooks/01_exploratory_data_analysis.ipynb::cell 23 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| sessions | plays | notebooks/01_exploratory_data_analysis.ipynb::cell 40; notebooks/01_exploratory_data_analysis.ipynb::cell 58 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| sessions | tracks | notebooks/01_exploratory_data_analysis.ipynb::cell 58 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| sessions | artists | notebooks/01_exploratory_data_analysis.ipynb::cell 58 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| sessions | genres | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| sessions | minutes | notebooks/01_exploratory_data_analysis.ipynb::cell 58 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| sessions | full_plays | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| sessions | friction_plays | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| sessions | top_artist | notebooks/01_exploratory_data_analysis.ipynb::cell 58 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| sessions | top_genre | notebooks/01_exploratory_data_analysis.ipynb::cell 58 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| sessions | top_source | notebooks/01_exploratory_data_analysis.ipynb::cell 58 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| sessions | start_hour | notebooks/01_exploratory_data_analysis.ipynb::cell 58 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| sessions | length | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| sessions | full_rate | notebooks/01_exploratory_data_analysis.ipynb::cell 58 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| sessions | friction_rate | notebooks/01_exploratory_data_analysis.ipynb::cell 58 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| sessions | time_block | notebooks/01_exploratory_data_analysis.ipynb::cell 40 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| sessions | session_type | notebooks/01_exploratory_data_analysis.ipynb::cell 40; notebooks/01_exploratory_data_analysis.ipynb::cell 58 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| features | track_key | src/music_analytics/build.py::make_life (L789); src/music_analytics/recommend.py::prepare (L116); src/music_analytics/recommend.py::make_candidates (L288); src/music_analytics/recommend.py::make_pairs (L320); notebooks/01_exploratory_data_analysis.ipynb::cell 39; notebooks/01_exploratory_data_analysis.ipynb::cell 66 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| features | track | src/music_analytics/build.py::make_life (L789); src/music_analytics/recommend.py::make_text (L93); src/music_analytics/recommend.py::prepare (L116); src/music_analytics/recommend.py::make_candidates (L288); src/music_analytics/recommend.py::make_pairs (L320) | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| features | artist | src/music_analytics/build.py::make_life (L789); src/music_analytics/recommend.py::role_reason (L67); src/music_analytics/recommend.py::make_text (L93); src/music_analytics/recommend.py::prepare (L116); src/music_analytics/recommend.py::make_matrix (L201); src/music_analytics/recommend.py::make_candidates (L288); src/music_analytics/recommend.py::make_pairs (L320); notebooks/01_exploratory_data_analysis.ipynb::cell 39; notebooks/01_exploratory_data_analysis.ipynb::cell 62; notebooks/01_exploratory_data_analysis.ipynb::cell 64 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| features | album | src/music_analytics/build.py::make_life (L789); src/music_analytics/recommend.py::make_text (L93); src/music_analytics/recommend.py::prepare (L116); src/music_analytics/recommend.py::make_matrix (L201); src/music_analytics/recommend.py::make_candidates (L288); src/music_analytics/recommend.py::make_pairs (L320); notebooks/01_exploratory_data_analysis.ipynb::cell 39; notebooks/01_exploratory_data_analysis.ipynb::cell 62 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| features | genre | scripts/make_eda.py::<module>; src/music_analytics/build.py::make_life (L789); src/music_analytics/recommend.py::role_reason (L67); src/music_analytics/recommend.py::make_text (L93); src/music_analytics/recommend.py::prepare (L116); src/music_analytics/recommend.py::make_matrix (L201); src/music_analytics/recommend.py::make_candidates (L288); src/music_analytics/recommend.py::make_pairs (L320); notebooks/01_exploratory_data_analysis.ipynb::cell 39; notebooks/01_exploratory_data_analysis.ipynb::cell 62; notebooks/01_exploratory_data_analysis.ipynb::cell 64 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| features | display | src/music_analytics/build.py::make_life (L789); src/music_analytics/recommend.py::make_text (L93); src/music_analytics/recommend.py::prepare (L116); src/music_analytics/recommend.py::make_candidates (L288); src/music_analytics/recommend.py::make_pairs (L320); notebooks/01_exploratory_data_analysis.ipynb::cell 62; notebooks/01_exploratory_data_analysis.ipynb::cell 64; notebooks/01_exploratory_data_analysis.ipynb::cell 66 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| features | plays | scripts/make_eda.py::<module>; src/music_analytics/build.py::make_life (L789); src/music_analytics/build.py::save_check (L882); src/music_analytics/recommend.py::role_reason (L67); src/music_analytics/recommend.py::prepare (L116); src/music_analytics/recommend.py::make_matrix (L201); src/music_analytics/recommend.py::make_candidates (L288); src/music_analytics/recommend.py::make_pairs (L320); notebooks/01_exploratory_data_analysis.ipynb::cell 62; notebooks/01_exploratory_data_analysis.ipynb::cell 64; notebooks/01_exploratory_data_analysis.ipynb::cell 66 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| features | minutes | scripts/make_eda.py::<module>; src/music_analytics/build.py::make_life (L789); src/music_analytics/build.py::save_check (L882); src/music_analytics/recommend.py::prepare (L116); src/music_analytics/recommend.py::make_matrix (L201); src/music_analytics/recommend.py::make_candidates (L288); src/music_analytics/recommend.py::make_pairs (L320); notebooks/01_exploratory_data_analysis.ipynb::cell 39; notebooks/01_exploratory_data_analysis.ipynb::cell 62; notebooks/01_exploratory_data_analysis.ipynb::cell 64 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| features | good_plays | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| features | full_plays | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| features | friction_plays | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| features | average_share | src/music_analytics/recommend.py::prepare (L116); src/music_analytics/recommend.py::make_matrix (L201); src/music_analytics/recommend.py::make_candidates (L288) | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| features | first_play | src/music_analytics/build.py::make_life (L789); src/music_analytics/build.py::save_check (L882); notebooks/01_exploratory_data_analysis.ipynb::cell 23; notebooks/01_exploratory_data_analysis.ipynb::cell 39; notebooks/01_exploratory_data_analysis.ipynb::cell 66 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| features | last_play | src/music_analytics/build.py::make_life (L789); src/music_analytics/build.py::save_check (L882); notebooks/01_exploratory_data_analysis.ipynb::cell 23 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| features | active_days | src/music_analytics/build.py::make_life (L789); src/music_analytics/recommend.py::prepare (L116); src/music_analytics/recommend.py::make_matrix (L201); src/music_analytics/recommend.py::make_candidates (L288); src/music_analytics/recommend.py::make_pairs (L320); notebooks/01_exploratory_data_analysis.ipynb::cell 62 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| features | source_count | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| features | source_top | notebooks/01_exploratory_data_analysis.ipynb::cell 62 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| features | role_top | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| features | track_id | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| features | apple_id | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| features | duration_milliseconds | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| features | library_plays | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| features | library_skips | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| features | added_at | notebooks/01_exploratory_data_analysis.ipynb::cell 23 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| features | release_at | notebooks/01_exploratory_data_analysis.ipynb::cell 23 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| features | playlist_count | src/music_analytics/recommend.py::prepare (L116); src/music_analytics/recommend.py::make_matrix (L201); src/music_analytics/recommend.py::make_candidates (L288) | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| features | good_rate | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| features | full_rate | scripts/make_eda.py::<module>; src/music_analytics/build.py::make_life (L789); src/music_analytics/recommend.py::prepare (L116); src/music_analytics/recommend.py::make_matrix (L201); src/music_analytics/recommend.py::make_candidates (L288); src/music_analytics/recommend.py::make_pairs (L320); notebooks/01_exploratory_data_analysis.ipynb::cell 62; notebooks/01_exploratory_data_analysis.ipynb::cell 64 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| features | friction_rate | src/music_analytics/build.py::make_life (L789); src/music_analytics/recommend.py::role_reason (L67); src/music_analytics/recommend.py::prepare (L116); src/music_analytics/recommend.py::make_matrix (L201); src/music_analytics/recommend.py::make_candidates (L288); src/music_analytics/recommend.py::make_pairs (L320); notebooks/01_exploratory_data_analysis.ipynb::cell 62; notebooks/01_exploratory_data_analysis.ipynb::cell 64 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| features | library_ready | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| features | retained | notebooks/01_exploratory_data_analysis.ipynb::cell 39; notebooks/01_exploratory_data_analysis.ipynb::cell 66 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| features | recommender_ready | scripts/make_eda.py::<module>; src/music_analytics/build.py::make_life (L789); src/music_analytics/build.py::save_check (L882); src/music_analytics/recommend.py::prepare (L116); src/music_analytics/recommend.py::make_candidates (L288); src/music_analytics/recommend.py::make_pairs (L320) | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| features | recency_days | src/music_analytics/recommend.py::prepare (L116) | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| features | plays_log | src/music_analytics/recommend.py::prepare (L116); src/music_analytics/recommend.py::make_matrix (L201) | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| features | minutes_log | src/music_analytics/recommend.py::prepare (L116); src/music_analytics/recommend.py::make_matrix (L201) | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| features | days_log | src/music_analytics/recommend.py::prepare (L116); src/music_analytics/recommend.py::make_matrix (L201) | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| features | playlist_log | src/music_analytics/recommend.py::prepare (L116); src/music_analytics/recommend.py::make_matrix (L201) | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| features | fresh_score | src/music_analytics/recommend.py::prepare (L116); src/music_analytics/recommend.py::make_matrix (L201) | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| features | keep_score | src/music_analytics/recommend.py::prepare (L116); src/music_analytics/recommend.py::make_matrix (L201) | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| features | affinity_score | src/music_analytics/build.py::make_life (L789); src/music_analytics/recommend.py::role_reason (L67); src/music_analytics/recommend.py::prepare (L116); src/music_analytics/recommend.py::make_matrix (L201); src/music_analytics/recommend.py::make_candidates (L288); src/music_analytics/recommend.py::make_pairs (L320); notebooks/01_exploratory_data_analysis.ipynb::cell 62; notebooks/01_exploratory_data_analysis.ipynb::cell 66 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| features | favorite_like | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| features | candidate_class | src/music_analytics/build.py::make_life (L789); src/music_analytics/recommend.py::make_text (L93); src/music_analytics/recommend.py::prepare (L116); src/music_analytics/recommend.py::make_matrix (L201); src/music_analytics/recommend.py::make_candidates (L288); src/music_analytics/recommend.py::make_pairs (L320); notebooks/01_exploratory_data_analysis.ipynb::cell 62; notebooks/01_exploratory_data_analysis.ipynb::cell 64 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| features | ready_reason | src/music_analytics/build.py::make_life (L789); src/music_analytics/recommend.py::make_text (L93); src/music_analytics/recommend.py::prepare (L116); src/music_analytics/recommend.py::make_candidates (L288); notebooks/01_exploratory_data_analysis.ipynb::cell 64 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| features | text | src/music_analytics/recommend.py::make_text (L93) | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| life | track_key | notebooks/01_exploratory_data_analysis.ipynb::cell 60 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| life | display | notebooks/01_exploratory_data_analysis.ipynb::cell 60 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| life | track | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| life | artist | notebooks/01_exploratory_data_analysis.ipynb::cell 60 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| life | album | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| life | genre | notebooks/01_exploratory_data_analysis.ipynb::cell 60 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| life | plays | notebooks/01_exploratory_data_analysis.ipynb::cell 60 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| life | minutes | notebooks/01_exploratory_data_analysis.ipynb::cell 60 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| life | active_days | notebooks/01_exploratory_data_analysis.ipynb::cell 60 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| life | first_play | notebooks/01_exploratory_data_analysis.ipynb::cell 23 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| life | last_play | notebooks/01_exploratory_data_analysis.ipynb::cell 23 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| life | full_rate | notebooks/01_exploratory_data_analysis.ipynb::cell 60 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| life | friction_rate | notebooks/01_exploratory_data_analysis.ipynb::cell 60 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| life | affinity_score | notebooks/01_exploratory_data_analysis.ipynb::cell 60 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| life | candidate_class | notebooks/01_exploratory_data_analysis.ipynb::cell 60 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| life | ready_reason | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| life | recommender_ready | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| life | stage | notebooks/01_exploratory_data_analysis.ipynb::cell 60 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| profile | metric | scripts/make_eda.py::<module>; src/music_analytics/build.py::save_check (L882) | EDA notebook cell 48 -> show_table (all columns) |
| profile | value | scripts/make_eda.py::<module>; src/music_analytics/build.py::save_check (L882) | EDA notebook cell 48 -> show_table (all columns) |
| profile | score | notebooks/01_exploratory_data_analysis.ipynb::cell 48 | EDA notebook cell 48 -> show_table (all columns) |
| recommend_candidates | track_key | scripts/show_recommendations.py::main (L9); notebooks/01_exploratory_data_analysis.ipynb::cell 69 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| recommend_candidates | display | scripts/show_recommendations.py::main (L9); src/music_analytics/recommend.py::find_track (L531) | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| recommend_candidates | track | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| recommend_candidates | artist | scripts/show_recommendations.py::main (L9); src/music_analytics/recommend.py::find_track (L531) | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| recommend_candidates | album | src/music_analytics/recommend.py::find_track (L531) | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| recommend_candidates | genre | scripts/show_recommendations.py::main (L9); src/music_analytics/recommend.py::find_track (L531) | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| recommend_candidates | plays | notebooks/01_exploratory_data_analysis.ipynb::cell 69 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| recommend_candidates | minutes | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| recommend_candidates | active_days | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| recommend_candidates | full_rate | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| recommend_candidates | friction_rate | scripts/show_recommendations.py::main (L9) | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| recommend_candidates | average_share | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| recommend_candidates | playlist_count | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| recommend_candidates | affinity_score | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| recommend_candidates | candidate_class | notebooks/01_exploratory_data_analysis.ipynb::cell 69 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| recommend_candidates | recommend_role | scripts/show_recommendations.py::main (L9); notebooks/01_exploratory_data_analysis.ipynb::cell 69 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| recommend_candidates | recommend_score | scripts/show_recommendations.py::main (L9); notebooks/01_exploratory_data_analysis.ipynb::cell 69 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| recommend_candidates | quality_score | notebooks/01_exploratory_data_analysis.ipynb::cell 69 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| recommend_candidates | risk_score | notebooks/01_exploratory_data_analysis.ipynb::cell 69 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| recommend_candidates | recommender_ready | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| recommend_candidates | ready_reason | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| recommend_candidates | recommend_reason | scripts/show_recommendations.py::main (L9) | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| recommendations | seed_track_key | src/music_analytics/recommend.py::recommend_for (L550) | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| recommendations | seed_display | notebooks/01_exploratory_data_analysis.ipynb::cell 70 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| recommendations | seed_track | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| recommendations | seed_artist | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| recommendations | seed_album | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| recommendations | seed_genre | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| recommendations | candidate_track_key | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| recommendations | candidate_display | scripts/show_recommendations.py::main (L9); notebooks/01_exploratory_data_analysis.ipynb::cell 70 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| recommendations | candidate_track | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| recommendations | candidate_artist | scripts/show_recommendations.py::main (L9) | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| recommendations | candidate_album | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| recommendations | candidate_genre | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| recommendations | similarity | scripts/show_recommendations.py::main (L9); src/music_analytics/recommend.py::recommend_for (L550); notebooks/01_exploratory_data_analysis.ipynb::cell 70 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| recommendations | recommend_role | scripts/show_recommendations.py::main (L9); notebooks/01_exploratory_data_analysis.ipynb::cell 70 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| recommendations | recommend_score | scripts/show_recommendations.py::main (L9); src/music_analytics/recommend.py::recommend_for (L550); notebooks/01_exploratory_data_analysis.ipynb::cell 70 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| recommendations | affinity_score | notebooks/01_exploratory_data_analysis.ipynb::cell 70 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| recommendations | plays | notebooks/01_exploratory_data_analysis.ipynb::cell 70 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| recommendations | minutes | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| recommendations | active_days | ZERO named downstream references found | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| recommendations | full_rate | notebooks/01_exploratory_data_analysis.ipynb::cell 70 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| recommendations | friction_rate | scripts/show_recommendations.py::main (L9); notebooks/01_exploratory_data_analysis.ipynb::cell 70 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| recommendations | candidate_class | notebooks/01_exploratory_data_analysis.ipynb::cell 70 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| recommendations | recommend_reason | scripts/show_recommendations.py::main (L9); notebooks/01_exploratory_data_analysis.ipynb::cell 70 | EDA notebook cell 26: missing-cell / duplicate-row QA (all columns) |
| recommend_profile | metric | notebooks/01_exploratory_data_analysis.ipynb::cell 68 | EDA notebook cell 68 -> show_table (all columns) |
| recommend_profile | value | notebooks/01_exploratory_data_analysis.ipynb::cell 68 | EDA notebook cell 68 -> show_table (all columns) |
| recommend_profile | description | ZERO named downstream references found | EDA notebook cell 68 -> show_table (all columns) |
| recommend_sample | track | ZERO named downstream references found | ZERO analytical consumers; load/registry only |
| recommend_sample | compare_track | ZERO named downstream references found | ZERO analytical consumers; load/registry only |
| recommend_sample | similarity | ZERO named downstream references found | ZERO analytical consumers; load/registry only |


## COLORS and palette

| Key | Value | Consumers | Finding |
|---|---|---|---|
| page | #EDF8FF | app/dashboard.py::style (L100) | Used |
| page_soft | rgba(237, 248, 255, 0.88) | app/dashboard.py::style (L100) | Used |
| ink | #17252D | app/dashboard.py::style (L100); app/dashboard.py::style_axes (L355); app/dashboard.py::section_heatmap (L682) | Used |
| black | #101010 | app/dashboard.py::style (L100) | Used |
| muted | #244F82 | app/dashboard.py::style (L100) | Used |
| select | #8B1230 | app/dashboard.py::style (L100) | Used |
| pink | #F5A8CD | app/dashboard.py::style (L100); app/dashboard.py::<module> | Used |
| cyan | #A8E8CE | app/dashboard.py::style (L100); app/dashboard.py::section_daily (L595); app/dashboard.py::section_heatmap (L682); app/dashboard.py::<module> | Duplicate of mint |
| mint | #A8E8CE | app/dashboard.py::<module> | Used |
| purple | #C5ADFF | app/dashboard.py::<module> | Used |
| yellow | #FFE28C | app/dashboard.py::section_daily (L595); app/dashboard.py::<module> | Used |
| coral | #F5A8CD | app/dashboard.py::section_daily (L595); app/dashboard.py::section_heatmap (L682) | Duplicate of pink |
| blue | #A9D6F5 | app/dashboard.py::style (L100) | Used |
| sky | #D3EBFB | None | ZERO consumers |
| sky_soft | rgba(211, 235, 251, 0.78) | app/dashboard.py::style (L100) | Used |
| sky_shade | rgba(150, 196, 232, 0.50) | app/dashboard.py::style (L100) | Used |
| wash | rgba(252, 200, 226, 0.30) | app/dashboard.py::style (L100) | Used |

PALETTE is consumed by section_overview, section_genres, section_recommend. Its final two entries (mint and cyan) are identical. Removing the duplicate changes color cycling after the fourth item, as explicitly requested.

## Every dashboard CSS class

| Class / class pattern | Consumer | Finding |
|---|---|---|
| stApp | app/dashboard.py::Streamlit root, all sections | Used (DOM rendering not executed) |
| block-container | app/dashboard.py::Streamlit main container | Used (DOM rendering not executed) |
| section-divider | app/dashboard.py::pink_divider | Used (DOM rendering not executed) |
| stMarkdown | app/dashboard.py::Streamlit markdown throughout | Used (DOM rendering not executed) |
| stTextInput | app/dashboard.py::section_recommend manual search | Used (DOM rendering not executed) |
| stTextArea | app/dashboard.py::section_recommend request | Used (DOM rendering not executed) |
| stMultiSelect | app/dashboard.py::No st.multiselect call | ZERO widget consumers; remove selector arm only |
| stButton | app/dashboard.py::section_genres, section_artists, section_recommend | Used (DOM rendering not executed) |
| hero | app/dashboard.py::hero | Used (DOM rendering not executed) |
| eyebrow | app/dashboard.py::hero and all sections | Used (DOM rendering not executed) |
| small-caps | app/dashboard.py::hero, section_overview | Used (DOM rendering not executed) |
| highlight | app/dashboard.py::hero | Used (DOM rendering not executed) |
| st-key-panel_* | app/dashboard.py::main: overview, genres, artists, repeat, daily, heatmap containers | Used (DOM rendering not executed) |
| metric-grid | app/dashboard.py::section_overview | Used (DOM rendering not executed) |
| metric | app/dashboard.py::metric -> section_overview | Used (DOM rendering not executed) |
| muted | app/dashboard.py::metric, section_recommend | Used (DOM rendering not executed) |
| metric-sub | app/dashboard.py::metric -> section_overview | Used (DOM rendering not executed) |
| kv | app/dashboard.py::section_overview | Used (DOM rendering not executed) |
| genre-row | app/dashboard.py::section_overview, section_genres | Used (DOM rendering not executed) |
| genre-row-top | app/dashboard.py::section_overview, section_genres | Used (DOM rendering not executed) |
| bar-bg | app/dashboard.py::section_overview, section_genres | Used (DOM rendering not executed) |
| bar-fill | app/dashboard.py::section_overview, section_genres | Used (DOM rendering not executed) |
| bubble | app/dashboard.py::section_artists | Used (DOM rendering not executed) |
| info-wrap | app/dashboard.py::info_card | Used (DOM rendering not executed) |
| info-card | app/dashboard.py::info_card | Used (DOM rendering not executed) |
| info-title | app/dashboard.py::info_card | Used (DOM rendering not executed) |
| info-line | app/dashboard.py::info_card | Used (DOM rendering not executed) |
| rank-chip | app/dashboard.py::section_recommend | Used (DOM rendering not executed) |
| st-key-player | app/dashboard.py::section_recommend container(key="player") | Used (DOM rendering not executed) |
| st-key-player_screen | app/dashboard.py::section_recommend container(key="player_screen") | Used (DOM rendering not executed) |

Additional non-class selectors: stHeader/header, headings and tab-list/tab/tab-panel/tab-highlight/tab-border are generated by main/hero/section headings; stCaptionContainer by section captions; textarea/input/base-input and placeholder/focus rules by section_recommend; stButton/BaseButton and pills/ButtonGroup by genre, repeat and recommendation controls; stProgress by section_repeat; stExpander by the selection UI; stAlert by section_heatmap fallback only (retire its explicit rules when that fallback is removed); stColumn/stHorizontalBlock by main and row layouts. Responsive selectors reuse the same consumers. Streamlit-generated selector compatibility is **not executed**.

## Proposed deletions — awaiting confirmation

| Proposed removal | Why / current consumer | Expected output effect (not executed) |
|---|---|---|
| Dashboard optional features read | No downstream use in dashboard; keep features producer for recommender/EDA | Less I/O; same current dashboard results |
| Dashboard hours read and timestamp/column guessing in build_heatmap_table | Fixed plays schema always supplies played_at; hours has hour, not any accepted bucket column | Replace with precomputed heatmap; keep hours for notebook |
| section_heatmap st.info fallback and dedicated stAlert rules | Schema failures move to data loading | Clear load-time error instead of an incomplete page |
| hero data argument | Body never reads it | No visual change |
| COLORS.sky; cyan/coral aliases; repeated cyan palette entry | sky has no consumers; aliases duplicate mint/pink | Same named colors; four-color cycling instead of five |
| .stMultiSelect selector arm | No multiselect widget | No current visual change |
| recommend.py Path import | No reference | None |
| build profile_type row and its save_check/make_eda references | Explicitly requested; scores have incompatible scales | Remove arbitrary label; keep notebook-consumed profile metrics |
| Schema-guessing/fallback branches, dashboard inline score, feature text duplication, redundant neighbor features, repeated neighbor display columns | Explicit replacements requested, not unused outputs | Fixed schema, single score source, slimmer neighbor artifact; notebook/CLI must join display data |
| Prompt/edit-history text; script sys.path hacks; import-time make_paths call | Explicit cleanup request | Neutral documentation; editable install and explicit output-directory setup required |

Conditional deletion requiring your decision: recommend_sample and sample_scores have no analytical consumer, but load_outputs currently requires the file and the notebook loads it. I propose removing the generator/output and those load-only references together. cosine_similarity becomes unused after sample_scores is removed.

Do not delete as dead: recommend.make_profile/recommend_profile (notebook cell 68 displays them); build.make_profile/profile metrics (cell 48 displays them); life, sources, sessions, hours (active notebook analyses). albums, playlists, library, playlist_tracks are at least schema-QA consumers; daily_tracks supports the build in memory and is loaded/date-converted in the notebook. Retiring persistence or schema-only consumers is a scope decision, not proof of no use.

show_recommendations.py is a runnable CLI, with find_track and recommend_for as dependencies. No repository file invokes that CLI, but this alone does not make an entry point dead. Confirm retirement or preservation; recommend_for logic is explicitly needed by the new dashboard selection list.

Model artifacts recommend_model.joblib and recommend_matrix.npz are written and announced by make_recommendations.py but no repository reader was found. recommend_settings.json is explicitly required by Phase 3. Confirm whether to retire the unused model/matrix persistence; fitting remains necessary for pair generation.

## Baseline from executed, unchanged builders

| Metric | Before | After |
|---|---|---|
| events | 10454 | Pending approved implementation |
| valid_plays_30s | 3743 | Pending approved implementation |
| minutes | 9900.943433333334 | Pending approved implementation |
| listening_days_UTC | 143 | Pending approved implementation |
| longest_day_UTC | 2026-01-01 00:00:00 | Pending approved implementation |
| longest_day_minutes | 331.87893333333335 | Pending approved implementation |
| peak_fixed_EST | Wednesday 20-24 EST | Pending approved implementation |
| top5_artists_events | [{'artist': 'ATEEZ', 'plays': 826}, {'artist': 'Spiritual Concepts', 'plays': 381}, {'artist': 'Yves', 'plays': 344}, {'artist': 'XG', 'plays': 256}, {'artist': 'IVE', 'plays': 223}] | Pending approved implementation |
| unknown_genre_event_share | 0.1506600344365793 | Pending approved implementation |
| unknown_genre_valid_play_share | 0.08121827411167512 | Pending approved implementation |
| match_tier_rates | Not recorded by current builder; not inferred from final metadata | Pending approved implementation |
| unknown_duration_share | 9.565716472163765e-05 | Pending approved implementation |

## Daily timestamp finding

make_daily calls as_day(date_played), which parses YYYYMMDD with utc=True, casts hours to integer, and adds that many hours. This assigns UTC without checking a timezone in the export. These synthesized timestamps do not determine the main plays timeline: make_plays uses activity-event timestamps and consumes daily only for metadata fallback. The inspected raw CSV has Date Played and Hours fields, with no timezone field. The source timezone of date_played/hours remains unverified; no UTC assumption should be carried into the refactor.

## Decisions required before implementation

1. Approve the deletion proposal, and decide whether notebooks remain supported consumers. Proposed approach: preserve their analytical sections, update schema-dependent reads, and remove load-only recommend_sample references.
2. Confirm America/New_York and display label ET.
3. Supply rolling cutoff dates, prediction-window length, and which earlier windows tune versus which later windows are held out. Current executed event range: 2025-10-18 00:35:42.673000+00:00 through 2026-03-13 22:20:48.734000+00:00. A 28-day test window must end inside the observed history; overlapping windows must be acknowledged.
4. Approve preserving the existing block weights text=1.00, categorical=0.85, numeric=1.25 after normalization, and existing mood/text boost coefficients, or specify replacements. These are existing values, not newly chosen values.
5. Specify/approve evaluation seed, tuning grid/objective, multi-selection neighbor aggregation/count, ranking-correlation population/tie rules, and minimum dependency versions other than the specified Streamlit minimum. None has been newly selected.
6. Clarify ambiguous daily-title behavior: if that tier maps to several artists but a later library-title tier is unique, must the play stay Unknown Artist or may it proceed to the unique later tier?
7. Confirm whether to remove the standalone show_recommendations CLI and unused saved model/matrix artifacts.

Phase 0 changelog: added this audit report and machine-readable baseline only; application behavior unchanged. No deletions or refactor edits performed.

## Additional reference checks

The empty src/data, src/features, src/recommender, src/utils, and src/visualization package stubs have no import consumers in application, script, source, README, or notebook searches. Proposed deletion: these five empty __init__.py files/directories. src/__init__.py only defines __version__ and has no identified consumer; propose removing it when packaging music_analytics under the src layout. Preserve src/music_analytics/__init__.py.

Installed versions observed: streamlit 1.63.0, pandas 2.3.3, pyarrow 25.0.1, plotly 7.0.0, scikit-learn 1.9.0, scipy 1.16.3, joblib 1.6.0, numpy 2.3.5. pytest is not installed. No new dependency minimums were selected and no packages were installed.

## Confirmed daily-table column retirement proposal

make_plays reads only daily.track_name, track_key, artist, album, genre, duration_milliseconds, plays, and minutes. The notebook converts date/played_at but performs no daily-table analysis. The written daily columns apple_id, track, hour, play_milliseconds, skips, source_type, end_reason, ignore_recs, track_id, artist_name, album_name, and skip_rate have no downstream column consumer. Propose removing them from the persisted daily schema while retaining temporary identity/duration fields needed to construct the eight consumed metadata fields and the notebook date fields. Remove the skip-rate calculation and source/end-reason/ignore-recommendations extraction entirely because their results have no consumer. This proposal does not remove the metadata fallback used by make_plays.
