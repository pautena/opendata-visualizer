from app.reader import get_deaths_df
from app.video import generate_deaths_video_from_df
import os 

def main():
    os.makedirs('tmp/frames',exist_ok=True)
    df = get_deaths_df()
    generate_deaths_video_from_df(df)




if __name__ == "__main__":
    main()