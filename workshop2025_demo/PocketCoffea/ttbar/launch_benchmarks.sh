sleep 120
pocket-coffea run --cfg analysis_config_benchmarking_small.py -ro run_options/run_options_infn.yml -e dask@infn-af -o output_small_1m -c 1000000
sleep 120
pocket-coffea run --cfg analysis_config_benchmarking_medium.py -ro run_options/run_options_infn.yml -e dask@infn-af -o output_medium_1m -c 1000000
sleep 120
pocket-coffea run --cfg analysis_config_benchmarking_large.py -ro run_options/run_options_infn.yml -e dask@infn-af -o output_large_1m -c 1000000