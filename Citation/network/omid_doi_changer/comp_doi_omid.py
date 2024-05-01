# doi , omid 매칭하는 코드
# 현재 가지고 있는 doi 와 opencitaiton omid(2024) 기준으로 다운 받은 파일과 비교하여 매칭되는 doi와 omid를 뽑아 매칭

import pandas as pd
import re

# 파일을 읽어들입니다.
paperlist_df = pd.read_csv('paperlist_doi.csv')
omid_df = pd.read_csv('omid.csv')

# 'omid.csv'의 'id' 열에서 DOI 값을 추출합니다.
# 이때, 'doi:' 뒤의 값을 추출하며, 'doi'가 없는 경우는 제외합니다.
omid_df['cleaned_doi'] = omid_df['id'].apply(lambda x: re.search(r'doi:(.+)', x, re.IGNORECASE).group(1).strip() if re.search(r'doi:(.+)', x, re.IGNORECASE) else None)

# 결과를 확인하기 위해 불필요한 값이 없는지 확인합니다.
print(omid_df[['omid', 'cleaned_doi']].dropna())

# 'DOI' 열과 'cleaned_doi' 열을 기준으로 두 DataFrame을 조인합니다.
result_df = pd.merge(paperlist_df, omid_df, left_on='DOI', right_on='cleaned_doi', how='inner')

# 최종 결과에서 필요한 열만을 선택합니다.
final_df = result_df[['DOI', 'omid']]

# 결과 확인
print(final_df)

# 결과를 CSV 파일로 저장
final_df.to_csv('matched_results.csv', index=False)
