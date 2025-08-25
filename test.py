
col = ["article", "test", "2"]

cols = ", ".join(col)
placeholders = ", ".join(["%s"] * len(col))

query = f"""
    INSERT INTO AAA ({cols})
    VALUES ({placeholders})
"""


print(query)

# print()