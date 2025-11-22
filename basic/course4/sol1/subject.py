import csv

def merge_csv_files(train_file, test_file, output_file):
    """
    외부 라이브러리 없이 순수 Python으로 train.csv와 test.csv를 병합하는 함수
    """
    # 병합된 데이터를 저장할 리스트
    merged_data = []
    
    # train.csv 읽기
    print("train.csv 파일을 읽는 중...")
    with open(train_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)  # 헤더 읽기
        
        # train 데이터에 'dataset' 컬럼 추가
        header_with_dataset = header + ['dataset']
        merged_data.append(header_with_dataset)
        
        train_count = 0
        for row in reader:
            # train 데이터임을 표시
            row_with_dataset = row + ['train']
            merged_data.append(row_with_dataset)
            train_count += 1
    
    print(f"train.csv에서 {train_count}개의 행을 읽었습니다.")
    
    # test.csv 읽기
    print("test.csv 파일을 읽는 중...")
    with open(test_file, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        test_header = next(reader)  # test 파일의 헤더 읽기 (Transported 컬럼 없음)
        
        test_count = 0
        for row in reader:
            # test 데이터에 Transported 컬럼 추가 (None 값으로)
            row_with_transported = row + ['']  # 빈 문자열로 추가
            # test 데이터임을 표시
            row_with_dataset = row_with_transported + ['test']
            merged_data.append(row_with_dataset)
            test_count += 1
    
    print(f"test.csv에서 {test_count}개의 행을 읽었습니다.")
    
    # 병합된 데이터를 새 파일에 저장
    print(f"병합된 데이터를 {output_file}에 저장하는 중...")
    with open(output_file, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerows(merged_data)
    
    print(f"병합 완료! 총 {len(merged_data)-1}개의 행이 저장되었습니다.")
    print(f"- train 데이터: {train_count}개")
    print(f"- test 데이터: {test_count}개")


def read_merged_csv(file_path):
    """
    병합된 CSV 파일을 읽어서 딕셔너리 형태로 반환하는 함수
    """
    data = {}
    
    with open(file_path, 'r', encoding='utf-8') as f:
        reader = csv.reader(f)
        header = next(reader)
        
        # 각 컬럼에 대한 빈 리스트 초기화
        for col in header:
            data[col] = []
        
        # 데이터 읽기
        for row in reader:
            for i, value in enumerate(row):
                data[header[i]].append(value)
    
    return data


def separate_train_test_data(merged_data):
    """
    병합된 데이터에서 train과 test 데이터를 분리하는 함수
    """
    train_data = {}
    test_data = {}
    
    # 헤더 정보 가져오기
    columns = list(merged_data.keys())
    dataset_col = merged_data['dataset']
    
    # 각 컬럼에 대한 빈 리스트 초기화
    for col in columns:
        if col != 'dataset':  # dataset 컬럼은 제외
            train_data[col] = []
            test_data[col] = []
    
    # 데이터 분리
    for i, dataset_type in enumerate(dataset_col):
        if dataset_type == 'train':
            for col in columns:
                if col != 'dataset':
                    train_data[col].append(merged_data[col][i])
        elif dataset_type == 'test':
            for col in columns:
                if col != 'dataset':
                    test_data[col].append(merged_data[col][i])
    
    return train_data, test_data


def analyze_transported_correlation(train_data):
    """
    Transported와 각 항목 간의 관련성을 분석하는 함수
    """
    print("\n=== Transported와 각 항목 간의 관련성 분석 ===")
    
    correlations = {}
    transported = train_data['Transported']
    
    # 범주형 변수들 분석
    categorical_columns = ['HomePlanet', 'CryoSleep', 'Destination', 'VIP']
    
    for col in categorical_columns:
        if col in train_data:
            print(f"\n[{col}] 별 Transported 비율:")
            
            # 각 카테고리별 통계 계산
            category_stats = {}
            total_count = 0
            
            for i, value in enumerate(train_data[col]):
                if value and transported[i]:  # 빈 값이 아닌 경우만
                    if value not in category_stats:
                        category_stats[value] = {'total': 0, 'transported': 0}
                    category_stats[value]['total'] += 1
                    if transported[i] == 'True':
                        category_stats[value]['transported'] += 1
                    total_count += 1
            
            # 비율 계산 및 출력
            max_diff = 0
            for category, stats in category_stats.items():
                ratio = stats['transported'] / stats['total'] if stats['total'] > 0 else 0
                print(f"  {category}: {stats['transported']}/{stats['total']} ({ratio:.3f})")
                
                # 전체 평균과의 차이 계산
                overall_ratio = sum(1 for t in transported if t == 'True') / len(transported)
                diff = abs(ratio - overall_ratio)
                max_diff = max(max_diff, diff)
            
            correlations[col] = max_diff
    
    # 수치형 변수들 분석
    numeric_columns = ['Age', 'RoomService', 'FoodCourt', 'ShoppingMall', 'Spa', 'VRDeck']
    
    for col in numeric_columns:
        if col in train_data:
            print(f"\n[{col}] 별 Transported 평균값:")
            
            transported_values = []
            not_transported_values = []
            
            for i, value in enumerate(train_data[col]):
                if value and value != '':  # 빈 값이 아닌 경우만
                    try:
                        num_value = float(value)
                        if transported[i] == 'True':
                            transported_values.append(num_value)
                        else:
                            not_transported_values.append(num_value)
                    except ValueError:
                        continue
            
            if transported_values and not_transported_values:
                avg_transported = sum(transported_values) / len(transported_values)
                avg_not_transported = sum(not_transported_values) / len(not_transported_values)
                
                print(f"  Transported=True 평균: {avg_transported:.2f}")
                print(f"  Transported=False 평균: {avg_not_transported:.2f}")
                print(f"  차이: {abs(avg_transported - avg_not_transported):.2f}")
                
                # 정규화된 차이 계산 (표준화)
                all_values = transported_values + not_transported_values
                std_dev = (sum((x - sum(all_values)/len(all_values))**2 for x in all_values) / len(all_values))**0.5
                normalized_diff = abs(avg_transported - avg_not_transported) / std_dev if std_dev > 0 else 0
                correlations[col] = normalized_diff
    
    # 관련성이 높은 순서로 정렬
    print(f"\n=== Transported와 관련성 높은 항목 순위 ===")
    sorted_correlations = sorted(correlations.items(), key=lambda x: x[1], reverse=True)
    
    for i, (col, correlation) in enumerate(sorted_correlations, 1):
        print(f"{i}. {col}: {correlation:.4f}")
    
    return correlations


def analyze_age_groups_transported(train_data):
    """
    연령대별 Transported 비율을 분석하고 텍스트 그래프로 출력하는 함수
    """
    print("\n=== 연령대별 Transported 비율 분석 ===")
    
    # 연령대별 통계 수집
    age_groups = {
        '10대': {'total': 0, 'transported': 0},
        '20대': {'total': 0, 'transported': 0},
        '30대': {'total': 0, 'transported': 0},
        '40대': {'total': 0, 'transported': 0},
        '50대': {'total': 0, 'transported': 0},
        '60대': {'total': 0, 'transported': 0},
        '70대': {'total': 0, 'transported': 0}
    }
    
    ages = train_data['Age']
    transported = train_data['Transported']
    
    for i, age_str in enumerate(ages):
        if age_str and age_str != '':
            try:
                age = float(age_str)
                
                # 연령대 분류
                if 10 <= age < 20:
                    group = '10대'
                elif 20 <= age < 30:
                    group = '20대'
                elif 30 <= age < 40:
                    group = '30대'
                elif 40 <= age < 50:
                    group = '40대'
                elif 50 <= age < 60:
                    group = '50대'
                elif 60 <= age < 70:
                    group = '60대'
                elif 70 <= age < 80:
                    group = '70대'
                else:
                    continue  # 0-9세, 80세 이상은 제외
                
                age_groups[group]['total'] += 1
                if transported[i] == 'True':
                    age_groups[group]['transported'] += 1
                    
            except ValueError:
                continue
    
    # 비율 계산 및 출력
    print(f"\n연령대별 통계:")
    print(f"{'연령대':<6} {'전체':<8} {'전송':<8} {'비율':<8} {'그래프'}")
    print("-" * 50)
    
    ratios = []
    for group, stats in age_groups.items():
        if stats['total'] > 0:
            ratio = stats['transported'] / stats['total']
            ratios.append(ratio)
            
            # 텍스트 바 그래프 (최대 20개 문자)
            bar_length = int(ratio * 20)
            bar = "█" * bar_length + "░" * (20 - bar_length)
            
            print(f"{group:<6} {stats['total']:<8} {stats['transported']:<8} {ratio:.3f} {bar}")
    
    # 텍스ト 기반 라인 그래프
    print(f"\n=== 연령대별 Transported 비율 라인 그래프 ===")
    
    # 그래프 높이 (10단계)
    graph_height = 10
    max_ratio = max(ratios) if ratios else 1
    
    # 위에서 아래로 그리기
    for level in range(graph_height, -1, -1):
        line = f"{level/graph_height:.1f} |"
        
        for group in age_groups.keys():
            if age_groups[group]['total'] > 0:
                ratio = age_groups[group]['transported'] / age_groups[group]['total']
                normalized_ratio = ratio / max_ratio if max_ratio > 0 else 0
                
                if normalized_ratio >= level / graph_height:
                    line += " ● "
                else:
                    line += "   "
            else:
                line += "   "
        
        print(line)
    
    # X축 레이블
    print("    +" + "-" * (len(age_groups) * 3))
    x_labels = "     "
    for group in age_groups.keys():
        x_labels += f"{group[0]:<3}"  # 첫 글자만 (1, 2, 3, ...)
    print(x_labels)
    print(f"\n범례: ● = 데이터 포인트, 최대값: {max_ratio:.3f}")


# 사용 예시
if __name__ == "__main__":
    # CSV 파일 병합
    merge_csv_files('train.csv', 'test.csv', 'merged_spaceship_titanic.csv')
    
    # 병합된 파일 읽기
    merged_data = read_merged_csv('merged_spaceship_titanic.csv')
    
    # 기본 정보 출력
    print(f"\n병합된 데이터 정보:")
    print(f"컬럼 수: {len(merged_data)}")
    print(f"컬럼명: {list(merged_data.keys())}")
    print(f"총 행 수: {len(merged_data['PassengerId'])}")
    
    # train과 test 데이터 분리
    train_data, test_data = separate_train_test_data(merged_data)
    
    print(f"\n분리된 데이터 정보:")
    print(f"train 데이터: {len(train_data['PassengerId'])}개 행")
    print(f"test 데이터: {len(test_data['PassengerId'])}개 행")
    
    # === 새로운 분석 기능 ===
    
    # 1. Transported와 관련성 높은 항목 찾기
    correlations = analyze_transported_correlation(train_data)
    
    # 2. 연령대별 Transported 비율 분석 및 그래프
    analyze_age_groups_transported(train_data)