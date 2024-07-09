#!/bin/bash

echo "|| Starting entire stack."

./stack_pre_process.sh
wait $!

./stack_groundtruth.sh
wait $!

./stack_dict_test.sh
wait $!

./stack_llm_test.sh
wait $!

echo "|| Executed entire stack."
