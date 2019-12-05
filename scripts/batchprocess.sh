NAMEu=iam_breta_wash
INPUT=/Users/gilfewster/Documents/AdvanceParty/AUSUP_Signature/handwriting_datasets/washington 
SAVE_IN_DIR=../writing_samples
PREFIX_OUTPUT_FNAME='washington_'
ASPECT=ignore
FILL_COLOR=0,0,0
WIDTH=32
HEIGHT=16
COLOR_MODE=m
THRESHOLD=220
NUMBER=0


NUMBER_SUMMARY=$([ $NUMBER -gt 0 ] && echo $NUMBER || echo all) 
OUTPUT="${SAVE_IN_DIR}/${NAME}_${NUMBER_SUMMARY}_${WIDTH}x${HEIGHT}_${COLOR_MODE}" 

echo 
echo "*** Converting $NUMBER_SUMMARY files ***"
echo "from: $INPUT"
echo "to:   $OUTPUT"
echo 

mkdir -p $OUTPUT

# run the processor
time python format_image.py \
-a $ASPECT \
-W $WIDTH \
-H $HEIGHT \
-c $COLOR_MODE \
-f $FILL_COLOR \
-i $INPUT \
-t $THRESHOLD \
-n $NUMBER \
-p $PREFIX_OUTPUT_FNAME \
-o $OUTPUT 
#-I \

