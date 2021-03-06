import sys,os
import re
import math
import string
from pdb import set_trace

class Tree:
    def __init__(self,u,vs):
        self.u = u
        self.vs = vs

    def distance(self,w):
        if w == self.u:
            return 0,[w]

        for v in self.vs:
            d,path = v.distance(w)
            if d != -1:
                return d+1,[self.u]+path

        return -1,[]

    def taxa(self):
        ret = set()

        if type(self.u) == type(""):
            ret.add(self.u)

        for v in self.vs:
            ret = ret.union(v.taxa())

        return ret

    def nodes(self):
        ret = set([self])

        for v in self.vs:
            ret = ret.union(v.nodes())

        return ret

    def level_traverse(self,ret=None):
        if ret == None:
            ret = []

        for v in self.vs:
            ret = v.level_traverse(ret)

        ret.append(self.u)

        return ret

    def splits(self):
        if len(self.vs) == 0:
            return []

        taxa = self.taxa()

        ret = []
        for v in self.vs:
            vt = v.taxa()
            delta = taxa.difference(vt)

            r = v.splits() #the split happen in subtrees
            ret += [(L,R.union(delta)) for L,R in r]

            ret.append((vt,delta))

        return ret

    def adj_list(self,father=None,cur=None,children=None):
        if cur == None:
            cur = {}
        if children == None:
            children = {}
        
        cur[self.u] = set()
        children[self.u] = set()
        if father != None:
            cur[self.u].add(father)

        for v in self.vs:
            cur,children = v.adj_list(father=self.u,cur=cur,children=children)
            cur[self.u].add(v.u)
            children[self.u].add(v.u)

        return cur,children

    def find_rev(self,dnas,pos,pre=None,mid=None):
        #print("find_rev:self=%s,pos=%d,pre=%s,mid=%s"
              #% (self.u,pos+1,str(pre),str(mid)))
        if pre == None:
            ret = []
            for v in self.vs:
                ret += v.find_rev(dnas,pos,dnas[self.u][pos],None)

            return ret

        elif mid == None:
            if dnas[self.u][pos] != pre:
                ret = []
                for v in self.vs:
                    ret += [[self] + path for path in v.find_rev(dnas,pos,pre,dnas[self.u][pos])]

                return ret
            else:
                #print("")
                return []

        else:
            if dnas[self.u][pos] == pre:
                #print("")
                return [[self]]
            elif dnas[self.u][pos] == mid:
                ret = []
                for v in self.vs:
                    ret += [[self] + path for path in v.find_rev(dnas,pos,pre,mid)]
                return ret
            else:
                #print("")
                return []

def newick_parse(s):
    def S():
        ret = None

        if s[S.pos] == "(":
            S.pos += 1

            label = S.N
            S.N += 1
            ret = Tree(label,[])

            ret.vs.append(S())
            while s[S.pos] == ",":
                S.pos += 1
                ret.vs.append(S())

            assert s[S.pos] == ")"
            S.pos += 1

            if s[S.pos] in string.ascii_letters or s[S.pos] == "_": # has label
                label = s[S.pos]
                S.pos += 1
                while s[S.pos] in string.ascii_letters or s[S.pos] == "_":
                    label += s[S.pos]
                    S.pos += 1

                ret.u = label

        elif s[S.pos] in string.ascii_letters or s[S.pos] == "_":
            label = s[S.pos]
            S.pos += 1
            while s[S.pos] in string.ascii_letters or s[S.pos] == "_":
                label += s[S.pos]
                S.pos += 1

            ret = Tree(label,[])
        else:
            label = S.N
            S.N += 1
            ret = Tree(label,[])
        
        return ret

    
    S.N = 1
    S.pos = 0
    return S()

def distance_tree(tree,x,y):
    _,p1 = tree.distance(x)
    _,p2 = tree.distance(y)

    i = 0
    while i < min(len(p1)-1,len(p2)-1):
        if p1[i] != p2[i]:
            break

        i += 1

    if i > 0:
        i -= 1

    if x in p2:
        r = len(p2) - p2.index(x) - 1
    elif y in p1:
        r = len(p1) - p1.index(y) - 1
    else:
        r = (len(p1)-1) + (len(p2)-1) - 2*i

    return r,p1,p2,i

def distance(s,x,y):
    tree = newick_parse(s)

    return distance_tree(tree,x,y)

def newick_tree_to_distance_matrix(tree):
    taxa = list(tree.taxa())
    d = {}

    for i in range(len(taxa)):
        for j in range(i+1,len(taxa)):
            d[taxa[i],taxa[j]] = d[taxa[j],taxa[i]] = distance_tree(tree,taxa[i],taxa[j])[0]

    for taxon in taxa:
        d[taxon,taxon] = 0

    return d,taxa

def distance_using_nw_distance(s,x,y):
    with open("sample.nwc","w") as f:
        f.write(s)

    line = os.popen("nw_distance -m m sample.nwc %s %s" % (x,y)).readlines()[0]
    line.strip()
    ret = re.split("[ \t]+",line)[1]

    return int(ret)

def edge_splits(t,taxa):
    splits = t.splits()
    splits = filter(lambda x:len(x[0]) != 1 and len(x[1]) != 1, splits)

    ret = []
    for split in splits:
        s = ""
        for i in range(len(taxa)):
            if taxa[i] in split[0]:
                s += "1"
            else:
                s += "0"

        ret.append(s)

    return ret

#output = ""
#with open("rosalind_nwck.txt","r") as f:
    #line = f.readline()
    #while line != "":
        #line = line.strip()
        #s = line

        #line = f.readline()
        #line = line.strip()
        #x,y = line.split(" ")

        #d,p1,p2,i = distance(s,x,y)
        #output += " %d" % d

        ##nw_d = distance_using_nw_distance(s,x,y)

        ##if d != nw_d:
            ##print(p1,len(p1))
            ##print(p2,len(p2))
            ##print(i)
            ##print(x,y,d,nw_d)

        #f.readline()
        #line = f.readline()

#print(output)

#assert(distance("(cat,dog);","cat","dog") == 2)
#assert(distance("(cat)dog;","cat","dog") == 1)

#==============================================================

#with open("rosalind_ctbl.txt","r") as f:
    ##nwk_s = "(dog,((elephant,mouse),robot),cat);"
    #nwk_s = f.read()
    #nwk_s.strip()

#print("\n".join(edge_splits(newick_parse(nwk_s))))
