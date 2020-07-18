
DATA_FOLDER="data"
MODEL_FOLDER="finetuning_results"
INPUT_FILE="all_data.txt"
SCRIPT_FILE="transformers/examples/language-modeling/run_language_modeling.py"

mkdir ./$DATA_FOLDER
mkdir ./$MODEL_FOLDER

pip install transformers tensorboardX --user

git clone https://github.com/huggingface/transformers.git
git checkout ba24001

gsutil cp gs://gpt2-finetuning-astro-storage/$INPUT_FILE ./$DATA_FOLDER/$INPUT_FILE

python ./$SCRIPT_FILE --train_data_file=./$DATA_FOLDER/$INPUT_FILE --model_type=gpt2 --model_name_or_path=gpt2 --line_by_line --do_train --per_gpu_train_batch_size=4 --num_train_epochs=1 --seed=101 --output_dir=./$MODEL_FOLDER

gsutil cp -r ./$MODEL_FOLDER/* gs://gpt2-finetuning-astro-storage/$MODEL_FOLDER/
