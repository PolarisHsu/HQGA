#!/bin/bash
NGPU=$1
MODE=$2
python main_qa.py \
	--ngpu $NGPU \
	--mode $MODE
