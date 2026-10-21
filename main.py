from model import preprocessing
from model import train_model
from model import predict
from model import reasons

if __name__ == "__main__":
    reasons.save_top_reasons(path="data/top_reasons.csv", top_n=5)
    print("Saved top reasons to data/top_reasons.csv")
    print("Pipeline complete.")
