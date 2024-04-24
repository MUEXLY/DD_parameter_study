txt = [[100,1,1], [200,2,2]]
#txt = [f'{str(i).replace(",","").strip("[]")}\n' for i in txt]
txt = [f'{str(text).replace(",", "").strip("[]")}' + ('\n' if idx < len(txt) - 1 else '') for idx, text in enumerate(txt)]
for j in txt:
    print(j)

#txt = [[100, 1, 1], [200, 2, 2]]
# Use enumerate to get both the index and the value in the list comprehension

