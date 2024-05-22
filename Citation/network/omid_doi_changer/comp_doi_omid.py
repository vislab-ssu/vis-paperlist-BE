# doi , omid 매칭하는 코드
# 현재 가지고 있는 doi 와 opencitaiton omid(2024) 기준으로 다운 받은 파일과 비교하여 매칭되는 doi와 omid를 뽑아 매칭

import pandas as pd
import re

paperlist_df = pd.read_csv('paperlist_doi.csv')
omid_df = pd.read_csv('omid.csv')

# omid에 들어있는 값들이 모두 소문자였음. 그래서 소문자로 변환 해주고 해야 함
paperlist_df['DOI'] = paperlist_df['DOI'].str.lower()

# 'omid.csv'의 'id' 열에서 DOI 값을 추출
omid_df['cleaned_doi'] = omid_df['id'].apply(lambda x: re.search(r'doi:(.+)', x, re.IGNORECASE).group(1).strip() if re.search(r'doi:(.+)', x, re.IGNORECASE) else None)

print(omid_df[['omid', 'cleaned_doi']].dropna())

result_df = pd.merge(paperlist_df, omid_df, left_on='DOI', right_on='cleaned_doi', how='inner')

final_df = result_df[['DOI', 'omid']]

print(final_df)

final_df.to_csv('matched_results.csv', index=False)
