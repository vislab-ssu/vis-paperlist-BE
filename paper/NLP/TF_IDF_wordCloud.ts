export function processWordCloud(input) {
  // 객체를 배열로 변환하고 값에 따라 정렬
  const items = Object.keys(input).map(function (key) {
    return { word: key, size: input[key] };
  });
  items.sort(function (a, b) {
    return b.size - a.size;
  });

  // 상위 10개 요소 추출
  const topItems = items.slice(0, 10);
  const totalSize = 300;
  const sum = topItems.reduce((acc, val) => {
    acc += val.size;
    return acc;
  }, 0);

  // wordcloud에 사용할 수 있는 형식으로 변환
  const myWords = topItems.map(function (item) {
    return { word: item.word, size: totalSize * (item.size / sum) }; // size를 조정하여 wordcloud에 적합하게 만들기
  });

  //   console.log(myWords);
  return { myWords };
}
