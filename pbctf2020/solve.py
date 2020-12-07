from z3 import *

globalBlockNr = 0
def blockify(line):
    global globalBlockNr
    blocks = [] # (blockType, blockSize, blockPostionVar)
    lastBlock = None
    for c in line:
        if lastBlock != None and (ord(c)-ord('0')) == lastBlock[0]:
            bT, bS, bV = lastBlock
            lastBlock = (bT, bS+1, bV)
        else:
            if lastBlock != None:
                blocks.append(lastBlock)
                lastBlock = None
            if c != '0':
                lastBlock = ((ord(c)-ord('0')), 1, BitVec('block_'+str(globalBlockNr), 8))
                globalBlockNr += 1
    if lastBlock != None: blocks.append(lastBlock)
    return blocks
    


pixel = [[BitVec('pixel_'+str(x)+"_"+str(y), 8) for x in range(0x32)] for y in range(0x32)]

s = Solver()


def blockifyConstrains(line):
    blocks = blockify(line)
    for i in range(len(blocks)):
        s.add(ULE(blocks[i][3],0x32-blocks[i][1])) # A Block may only have a position from 0 to 49 and they may not go out of bounds

    for i in range(len(blocks)):
        if i+1 < len(blocks) and blocks[i][0] == blocks[i+1][0]: s.add(ULT(blocks[i][2]+blocks[i][1], blocks[i+1][2])) # Increasing the boundry box if two same Type Blocks are following each other
        elif i+1 < len(blocks): s.add(ULE(blocks[i][2]+blocks[i][1], blocks[i+1][2])) # No Block may intersect or be more right than their successor Block
        
        if i-1 > 0 and blocks[i][0] == blocks[i-1][0]: s.add(ULT(blocks[i-1][2]+blocks[i-1][1], blocks[i][2])) # Increasing the boundry box if two same Type Blocks are following each other
        elif i-1 > 0: s.add(ULE(blocks[i-1][2]+blocks[i-1][1], blocks[i][2])) # No Block may intersect or be more left than their predecessor Block
        
    return blocks

def addLine(line, row):
    blocks = blockifyConstrains(line)
        
    for p in range(0x32): # for each pixel in this row
        l = []
        last = (pixel[row][p] == 0) # if this pixel is in no block then it's value is 0
        for i in range(len(blocks)): # check if the pixel is in a block and if not check the next block
            last = If(And(ULE(blocks[i][2], p), ULT(p, blocks[i][2]+blocks[i][1])), pixel[row][p] == blocks[i][0], last)
        s.append(last) # add the merged constraint to the solver
    
def addColumn(line, col): 
    blocks = blockifyConstrains(line)
        
    for p in range(0x32): # for each pixel in this column
        l = []
        last = (pixel[p][col] == 0) # if this pixel is in no block then it's value is 0
        for i in range(len(blocks)): # check if the pixel is in a block and if not check the next block
            last = If(And(ULE(blocks[i][2], p), ULT(p, blocks[i][2]+blocks[i][1])), pixel[p][col] == blocks[i][0], last)
        s.append(last) # add the merged constraint to the solver
    
    
tableX = """11113111122221121011313331211113333322110111100000
11132112111223120213333111213131133313311111200000
10131121111112311231222321133121303331110100000000
11211112221232331230313231132312111223121320000000
11220223202223101133113111111211112131330000000000
32332131101123310112332311113311213112311110000000
23032323132220221311213111101321220222221310000000
12112211122311121111011122202212110131223222000000
12233232230323321221312322233101121322132220000000
20233111233121231133110121313323321322211110000000
33211121333321122132222111013313030320221130000000
12133313332211202332331133323221111322221312000000
13233033332312311111223333131123322313111200000000
11122233033223213321111333333221011011213110000000
21133303110133113231221311311132132023330000000000
11231222111120212222202232331312223211120233100000
32231112123311101332022120223111230313312233310000
23333121210122121332121222133121331232312023000000
22221131222231211101111211112133112123122310000000
12131323112210111111113311222233112021113331200000
22332133331132101122111111311211121012221111303200
22121233321112111112212131212112233211111320000000
31013312311231112312132232223113331122130000000000
33110101113231330322221322130331113212322200000000
11111211122231132221311332310131132331113332000000
12133202022222221112211321222333233111323200000000
20221321322331333031123322311222113333333333000000
22213133223223113311223312022322223033123033200000
23313032101011122122220222113123212121333030331000
23333222231122132021121013332122233233233000000000
22121332212312211122211012112333132223332222022000
31211010112311112212311012112332123122202230000000
11221133112222123231113232321111012133321321221000
11333122131010111331111112121133213221101221211000
11331322130311122111331010132333111012122210000000
31331101132332131221233122233133231211311223000000
11121322222321333123112222313211333221121330000000
32023032202311112112122222213323033320212232000000
13213233313111121333223121213202113113211333000000
11111312221123131223130332311322222112312321100000
11112311211211113030333133202332111111230310000000
11111332332112313123222311210132023113101131331000
11112323322333330321331323311113123310000000000000
11101133213311122111231111130331312112333110000000
22111101233202311312331131112333303222330333300000
32121122311123311332233333332212133133332300000000
12112333331101312322330321313202111313303323220000
12323211011211320211131121012312112232121123300000
20212222231120233131012332132311112222121113230000
32113333033133031221123122112331101131132230000000""".split("\n")
    
for row in range(0x32):
    addLine(tableX[row], row)
    
tableYB = """11113111122223112111133313331231111133333221111111
11132112111221123212331211121310231133301331111120
01213110211112121123133122321111133121132233321131
11211112221232331001132332331113231211121313130132
11223223320221233121112311011122112121111011231311
33132212011012332133111132311113333111022322221131
22233231313220321111122031121232222211121301222122
12213223112222110322330111122333323331101322013222
13130311223313021331132213121313033131321222213213
22223111213331120102233112111021331133023202231112
33133113332312321233331123132323111113332222130102
11132333333231321230221111322323113132131123131111
10223233033222101123301211133321322211011322133111
11313322311113221212123211303111311222111222203123
23223111211131131012121223233212222232313313033311
12123102222023221213231221212222111133322323222332
32332113132112110111211121211132131311121221132332
22120133132232221112210101131122331232122211113022
12132133201111123111211120323321320123332111113330
23131133332121113111122211131201111121311112130302
23121211311123103132233112203222321321123321133232
31210310232303212222221213132232211223323321102332
12311221123222320222210113333033223222313311233313
12113332101023132333111211113213312232130313130332
22222133222213112332332212213123301111233331133323
23313132121231121123111120211131113212332032322322
22313333211031211112222312133231122332303332221223
21323133111231112122101321221223111312232333021011
31121101213221221323121121101111112233121331222221
11221033211212122113313111022131131223311211211221
11231112012231121211111223120232333333231111012233
11133232222323311312313111222012332232133202212203
31131310233022311333230231232232103111313213221232
13112312321302301112123313232213232211313221313113
13102331311221313112213012231133032311311112121331
11113312332210322122212332321301222311131231133311
11111113232131221111211232111232322113010111233231
11112131203213313312331003111112333303121101133321
11111122331203311130223233133101232201122313232331
21312303333012011122013331111002213100113233201023
32201222330212331131023333313102021200313313331303
12011332213110131033021301223100231100322211322302
12021023323112011123020133103100311100223202310003
22012030100110033332011113302100033000210103210303
30021000200100033001020123102000000000100000120203
02010000300300030031000023002000000000000000000300
00010000000000020000000003000000000000000000000000
00000000000000020000000000000000000000000000000000
00000000000000030000000000000000000000000000000000
00000000000000000000000000000000000000000000000000""".split("\n")

tableY = []
for col in range(0x32):
    line = ""
    for indx in range(0x32):
        line += tableYB[indx][col] 
    tableY.append(line)

for col in range(0x32):
    addColumn(tableY[col], col)
    

while (s.check()):
    m = s.model()

    o = ""
    for y in range(0x32):
        l = ""
        for x in range(0x32):
            v = m[pixel[y][x]]
            if v == None:
                v = 'X'
            else:
                v = chr(ord('0')+int(v.as_long()))
            l = l + v
        o = o + l + "\n"
    print(o)
    s.add(Or([Or([m[pixel[y][x]] != pixel[y][x] for x in range(0x32) if m[pixel[y][x]] != None]) for y in range(1)]))

        
