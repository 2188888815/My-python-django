from Crypto.Hash import SHA256

'''
SHA-256 算法属于密码 SHA-2 系列哈希。 它产生了一个消息的 256 位摘要。
哈希值用作表示大量数据的固定大小的唯一值。 两组数据的哈希值仅在相应数据也匹配时才应当匹配。
数据的少量更改会在哈希值中产生不可预知的大量更改。
'''
hash = SHA256.new()
hash.update(b'message')
h = hash.digest()
#h = hash.hexdigest()
x = hash.hexdigest()
print(h)
print(x)