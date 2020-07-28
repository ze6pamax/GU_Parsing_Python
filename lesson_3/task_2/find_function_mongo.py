from pymongo import MongoClient

#connection parametrs
client = MongoClient('localhost', 27017)
db = client['vacancy_db']
hh_vac = db.hh

def find_salary(value):
    salaries=[]
    value_to_find = value
    salary_result = hh_vac.find({'$or':[{'min_salary':{'$gt':value_to_find}},{'max_salary':{'$gt':value_to_find}}]})
    for salary in salary_result:
        print(salary)
        salaries.append(salary)
    return salaries

def main():
    with open('/home/zebramax/geek_brains/GU_Parsing_Python/practice/lesson_3/find_salary_def_result.txt','w') as f:
        salaries = find_salary(270000)
        for salary in salaries:
            f.write("%s\n" % str(salary))

if __name__ == "__main__":
    main()