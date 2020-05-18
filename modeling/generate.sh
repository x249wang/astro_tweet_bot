
MODEL_FOLDER="finetuning_results"
SCRIPT_FILE="transformers/examples/run_generation.py"
OUTPUT_FOLDER="output"
OUTPUT_FILE="bot_tweets_raw.txt"
PROMPTS_FILE="prompts.txt"

mkdir ./$MODEL_FOLDER
mkdir ./$OUTPUT_FOLDER

pip install transformers tensorboardX --user

git clone https://github.com/huggingface/transformers.git

gsutil cp -r gs://gpt2-finetuning-astro-storage/$MODEL_FOLDER ./$MODEL_FOLDER

n=1
while read line; do
python ./$SCRIPT_FILE --model_type=gpt2 --model_name_or_path=./$MODEL_FOLDER --length=50 --prompt="$line" --num_return_sequences=10 --stop_token=! --temperature=1.0 --seed=100 >> ./$OUTPUT_FOLDER/$OUTPUT_FILE
n=$((n+1))
done < ./$PROMPTS_FILE

gsutil cp ./$OUTPUT_FOLDER/$OUTPUT_FILE gs://gpt2-finetuning-astro-storage/$OUTPUT_FOLDER/$OUTPUT_FILE
