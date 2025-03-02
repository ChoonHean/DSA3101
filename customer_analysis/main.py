import json
import datasets



def main():
    reviews = datasets.load_dataset(
        "McAuley-Lab/Amazon-Reviews-2023", f"raw_review_All_Beauty", trust_remote_code=True)["full"]
    print(type(reviews))
    for i in reviews:
        print(i)
        break

if __name__ == "__main__":
    main()