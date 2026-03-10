@echo off
echo ?? Starting LoyaSense Predictive Pipeline...
python generate_data.py
python src/features.py
python train_model.py
python predict.py
python action_plan.py
echo ? Pipeline Complete. Check data/top_50_loyalty_list.csv for results.
pause
