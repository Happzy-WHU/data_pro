import os
import json

from itertools import groupby
from random import shuffle
from collections import defaultdict

answers_dir = "A 组人工评测-500组3个候选答案"
answers_files = os.listdir(answers_dir)

dest_dir = "prod"
if not os.path.exists(dest_dir):
    os.makedirs(dest_dir)

def make_history(group):
    personality = group[0]["personality"]
    order_list = []
    ret = [{"role":personality}, {"tag": "[system](#additional_instructions)", "text": "请开始聊天吧！"}]
    
    for index, item in enumerate(group):
        question = item["question"]
        answers = item["generated"]
        ret.append({"tag": "[user](#message)", "text": question})
        order = list(range(len(answers)))
        shuffle(order)
        for i in range(len(answers)):
            ret.append({"tag": "[assistant](#message)", "text": f"@chatbot-0.{i}  "+answers[order[i]]})
        if index != len(group) - 1:
            ret.append({"scores": []},)
        else:
            ret.append({"lastScores": []},)
        order_list.append(order)
    return order_list, ret
            
data = []
for file in answers_files:
    with open(os.path.join(answers_dir, file), "r", encoding="utf-8") as f:
        temp_data = f.readlines() 
        temp_data = [json.loads(line) for line in temp_data]
        data.extend(temp_data)

results = []
part_len = len(data)//len(answers_files)
for i in range(part_len):
    results.append({"personality":data[i]["personality"], "question":data[i]["question"], "generated":[data[i]["generated"], data[i+part_len]["generated"], data[i+2*part_len]["generated"]]})

groups = defaultdict(list)
for p in results:
    groups[p['personality']].append(p)

for group in groups.values():
    order_list, history = make_history(group)
    order_list = [{"chatbot-0.0":item[0], "chatbot-0.1":item[1], "chatbot-0.2":item[2]} for item in order_list]
    with open(os.path.join(dest_dir, f'{group[0]["personality"]}_order.txt') , "w", encoding="utf-8") as f:
        json.dump(order_list, f, ensure_ascii=False, indent=4)
    with open(os.path.join(dest_dir, f'{group[0]["personality"]}_history.json'), "w", encoding="utf-8") as f:
        json.dump(history, f, ensure_ascii=False, indent=2)
