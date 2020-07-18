from app.reader import get_confirmed_cases_ccaa_df
from app.video import generate_ccaa_video_from_df
import os 

def main():
    os.makedirs('tmp/frames',exist_ok=True)
    df = get_confirmed_cases_ccaa_df()
    print(df.head())
    generate_ccaa_video_from_df(df)




if __name__ == "__main__":
    main()