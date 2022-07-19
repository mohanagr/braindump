import numpy as np
import time

def get_num_missing(s_idx, e_idx, missing_loc, missing_num):

    sum = 0
    blocks=[]
    for i, loc in enumerate(missing_loc):

        loc_end = loc + missing_num[i]
        
        if(loc>=s_idx):
            if(loc_end<=e_idx):
                sum+=missing_num[i]
                blocks.append([loc-s_idx,loc_end-s_idx])
            else:
                if(loc < e_idx):
                    sum += e_idx - loc
                    blocks.append([loc-s_idx,e_idx-s_idx])
                else:
                    break
        else:
            if(loc_end>s_idx):
                if (loc_end <= e_idx):
                    sum+= loc_end - s_idx
                    blocks.append([0,loc_end-s_idx])
                else:
                    sum+= e_idx - s_idx
                    blocks.append([0,e_idx-s_idx])
                    break
    print("missing blocks, localized values:", blocks)
    return sum, blocks

def get_rows_from_specnum(spec1,spec2, spec_num, spectra_per_packet):

    print(f"received spec1 = {spec1} and spec2 = {spec2}")
    l = np.searchsorted(spec_num,spec1,side='left')
    r = np.searchsorted(spec_num,spec2,side='left')
    # print(f"spec1={spec1} spec2={spec2}")
    # print(f"spec_num len {spec_num.shape[0]}, last spec_num {spec_num[-1]}, l={l}, r={r}")
    print(l,r)
    diff1=-1
    diff2=-1
    if(l<spec_num.shape[0]):
        diff1 = spec1-spec_num[l]
    if(r<spec_num.shape[0]):
        diff2 = spec2-spec_num[r] # will give distance from right element in not equal cases

    if(diff1!=0 and diff2!=0):
        diff1 = spec1-spec_num[l-1]
        diff2 = spec2-spec_num[r-1]
        print(diff1,diff2,"diffs")
        if(diff1<spectra_per_packet):
            idx1=(l-1)*spectra_per_packet+diff1
        else:
            idx1=l*spectra_per_packet
        if(diff2<spectra_per_packet):
            idx2=(r-1)*spectra_per_packet+diff2
        else:
            idx2=r*spectra_per_packet
    elif(diff1==0 and diff2!=0):
        idx1 = l*spectra_per_packet
        diff2 = spec2-spec_num[r-1]
        if(diff2<spectra_per_packet):
            idx2=(r-1)*spectra_per_packet+diff2
        else:
            idx2=r*spectra_per_packet
    elif(diff1!=0 and diff2==0):
        idx2 = r*spectra_per_packet
        diff1 = spec1-spec_num[l-1]
        if(diff1<spectra_per_packet):
            idx1=(l-1)*spectra_per_packet+diff1
        else:
            idx1=l*spectra_per_packet
    else:
        idx1 = l*spectra_per_packet
        idx2 = r*spectra_per_packet
    return int(idx1),int(idx2)

def get_common_rows(missing_blocks1,missing_num1, missing_blocks2,missing_num2, acclen):

    st=0
    b1=len(missing_blocks1)
    b2=len(missing_blocks2)
    # print("Block lens", b1, b2)
    if(len(missing_blocks1)>0):
        en=missing_blocks1[0][0]
    else:
        en=acclen
    if(b2==0):
        return np.arange(0,acclen-missing_num1)
    j=0
    i=0
    cum_missing=0
    tot=0
    ids=[]
    while(i<b1 and j<b2):
        en=missing_blocks1[i][0]
        # print("en is",en)
        if(missing_blocks2[j][0]<=en and missing_blocks2[j][1]>st):
            if(missing_blocks2[j][0]>st):
                if(missing_blocks2[j][1]>=en):
                    print("flag 1")
                    ids.append([st-cum_missing,missing_blocks2[j][0]-cum_missing])
                    tot+=(missing_blocks2[j][0]-st)
                    st=missing_blocks1[i][1]
                    cum_missing+=(missing_blocks1[i][1]-missing_blocks1[i][0])
                    i+=1
                else:
                    # print("flag 2")
                    ids.append([st-cum_missing,missing_blocks2[j][0]-cum_missing])
                    tot+=(missing_blocks2[j][0]-st)
                    st=missing_blocks2[j][1]
                    j+=1
            else:
                if(missing_blocks2[j][1]>=en):
                    # print("flag 3")
                    st=missing_blocks1[i][1]
                    cum_missing+=(missing_blocks1[i][1]-missing_blocks1[i][0])
                    i+=1 #whole present block1 is useless.
                else:
                    # print("flag 4")
                    st=missing_blocks2[j][1]
                    j+=1
        else:
            ids.append([st-cum_missing,en-cum_missing])
            tot+=(en-st)
            st=missing_blocks1[i][1]
            cum_missing+=(missing_blocks1[i][1]-missing_blocks1[i][0])
            # print("flag 5")
            i+=1
    # print("PHASE 1: st is",st,"and end is",en,"cum missing is",cum_missing, "i and j", i,j)
    # print("PHASE 1 ids",ids)
    
    en=acclen
    while(j<b2):
        if(missing_blocks2[j][0]<en and missing_blocks2[j][1]>st):
            if(missing_blocks2[j][0]>st):
                if(missing_blocks2[j][1]==en): #can't be greater anymore. looking at last present block
                    # print("flag 1")
                    ids.append([st-cum_missing,missing_blocks2[j][0]-cum_missing])
                    tot+=(missing_blocks2[j][0]-st)
                else:
                    # print("flag 2")
                    ids.append([st-cum_missing,missing_blocks2[j][0]-cum_missing])
                    tot+=(missing_blocks2[j][0]-st)
                    st=missing_blocks2[j][1]
                    if(j==(b2-1)):
                        ids.append([st-cum_missing,acclen-cum_missing])
            else:
                if(missing_blocks2[j][1]<en):
                    # print("flag 4")
                    st=missing_blocks2[j][1]
                    if(j==(b2-1)):
                        ids.append([st-cum_missing,acclen-cum_missing])
                        tot+=(acclen-st)
                    # print("here 2")
        else:
            ids.append([st-cum_missing,acclen-cum_missing]) 
            tot+=(acclen-st)
        
        j+=1
    while(i<b1):
        # print("i again")
        en=missing_blocks1[i][0]
        ids.append([st-cum_missing,en-cum_missing])
        tot+=(en-st)
        st=missing_blocks1[i][1]
        cum_missing+=(missing_blocks1[i][1]-missing_blocks1[i][0])
        if(i==(b1-1)):
            ids.append([missing_blocks1[i][1]-cum_missing,acclen-cum_missing])
        i+=1
    # print("DONE")
    arr=np.zeros(tot)
    n=0
    # print(ids)
    for i,b in enumerate(ids):
        arr[n:n+(b[1]-b[0])]=np.arange(b[0],b[1])
        n=b[1]-b[0]
    return arr,tot

    # print("st is",st,"and end is",en,"cum missing is",cum_missing, "i and j", i,j)
    # while(i<b1):
    #     if(i==(b1-1)):
    #         en=acclen
    #     ids.append([st-cum_missing,en-cum_missing])
    #     st=missing_blocks1[i][1]
    #     cum_missing+=(missing_blocks1[i][1]-missing_blocks1[i][0])
    #     i+=1
    # while(j<b2)




    

# np.random.seed(42)
# x=np.zeros(4000000,dtype='bool')

# missing_loc=np.random.randint(0,3999999,size=24)
# missing_loc.sort()
# missing_num=np.random.randint(50,2000,size=24)


spec_num = np.loadtxt('./spec_idx.txt',dtype='int')
missing_loc = np.loadtxt('./missing_loc.txt',dtype='int')
missing_num = np.loadtxt('./missing_num.txt',dtype='int')

spectra_per_packet = 5

x=np.zeros(spec_num[-1]+spectra_per_packet,dtype='bool')

for i,loc in enumerate(missing_loc):
    # print("range is ", loc, "to", loc+missing_num[i])
    x[loc:loc+missing_num[i]]=1

print("missing loc is ",missing_loc)
print("missing num is ",missing_num)
# print(missing_num.sum())

sum1,block1=get_num_missing(100000,400000,missing_loc,missing_num)
sum2,block2=get_num_missing(1900000,2200000,missing_loc,missing_num)
# block1=[[20,40],[60,80]]
# block1=[]
# block2=[[30,45],[50,60]]
# block1=[[20,40],[60,80]]
# block2=[[10,90]]
# block1=[[20,80]]
# block2=[[20,80]]
# block1=[[40,60]]
# block2=[[50,100]]
# block1=[[40,60]]
# block2=[[50,55]]
# sum1=0
# sum2=0
# for b in block1:
#     sum1+=(b[1]-b[0])
# for b in block2:
#     sum2+=(b[1]-b[0])
print(sum1,sum2)
tarr=np.zeros(20)
for i in range(20):
    t1=time.time()
    ids,tot=get_common_rows(block1,sum1,block2,sum2,300000)
    t2=time.time()
    tarr[i]=t2-t1
print(tarr.mean(),tarr.std())
print(tot)

# T1=0
# T2=0
# for i in range(0,10):
#     idxstart=i*393216
#     idxend=(i+1)*393216
#     if(idxend>spec_num.shape[0]*5):
#         idxend=spec_num.shape[0]*5
#     print(f"\nidxstart={idxstart}, idxend={idxend}")
#     t1=time.time()
#     s=get_num_missing(idxstart,idxend,missing_loc,missing_num)
#     rowstart,rowend = get_rows_from_specnum(idxstart,idxend,spec_num,spectra_per_packet)
#     print(rowstart,rowend)
#     t2=time.time()
#     T1+=t2-t1
#     t1=time.time()
#     y=x[idxstart:idxend].sum()
#     t2=time.time()
#     T2+=t2-t1
#     print(f"missing from func {s} and actual {y}. Missing+added = {s + rowend-rowstart}")
# print("average time taken for func",T1/10)
# print("average time taken for sum",T2/10)




