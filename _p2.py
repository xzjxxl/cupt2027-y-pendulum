import io
p="lab.html"; s=io.open(p,encoding="utf-8").read()
s=s.replace('<span id="v-th">','<span id="v-th0">')
s=s.replace('<span id="v-ph">','<span id="v-ph0">')
s=s.replace('<span id="v-g">','<span id="v-gam">')
io.open(p,"w",encoding="utf-8").write(s)
print("ids fixed")
