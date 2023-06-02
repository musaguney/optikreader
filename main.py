import cv2 as cv
import numpy as np
import utility as ut
import csv
import os


# burada fotografın belirli bir eşik değerıne göre eşiklenmesi sağlanıyor
# daha net değerler siyah beyaz görebilmek adına
# siyah olan alan beyaz , beyaz olan alan sıyaha donduruldu
# alt kısımda sıyah olmama sayısını nulmak adına
def esikle(img):
    img = cv.cvtColor(img,cv.COLOR_BGR2GRAY) # fotografı gri tona ayarlıyor
    return cv.adaptiveThreshold (img,255,cv.ADAPTIVE_THRESH_GAUSSIAN_C,cv.THRESH_BINARY_INV,21,2) # adaptive threshhold ile yogunluga göre eşikleme yapılıyor

# cevap kısımlarının ve ögrnonun kırpılmasını gercekleştirdik.
def ilkOn(img):
    return esikle(img[134:400,290:400])
def ikiOn(img):
    return esikle(img[134:400,455:565])
def ucOn(img):
    return esikle( img[134:400,615:725])
def dortOn(img):
    return esikle(img[134:400,775:885])
def ogrNo(img):
    return esikle(img[134:400,0:250])

# tum cevapları tek bir diziye atama işlemi gercekleşiyor
def allanswer(img):
    answers =[]
    ans1 = ilkOn(img) 
    ans1 = cv.resize(ans1,(110,270)) # resize ile foto boyutunu tam sayıya esitledim
    sp1 = np.vsplit(ans1,10) # ilk onluk cevabı tek 10 a kesme işlemi gercekleşiyor
    for i in sp1:
        answers.append(i) # her soru için kesme işlemi gerceklesen fotoyu answera ekle 
    # alt kısımlarda aynı
    ans2 = ikiOn(img)
    ans2 = cv.resize(ans2,(110,270))
    sp2 = np.vsplit(ans2,10)
    for i in sp2:
        answers.append(i)
    ans3 = ucOn(img)
    ans3 = cv.resize(ans3,(110,270))
    sp3 = np.vsplit(ans3,10)
    for i in sp3:
        answers.append(i)
    ans4 = dortOn(img)
    ans4 = cv.resize(ans4,(110,270))
    sp4 = np.vsplit(ans4,10)
    for i in sp4:
        answers.append(i)
    return answers
def ogrnoBul(img):
    ogrno = ogrNo(img)
    ogrno = cv.resize(ogrno,(250,270))
    coloums = np.hsplit(ogrno,10) # ogrno için dikey kesim gercekleşiyor
    no = 0
    #bu döngüde ögrnonun tum haneleri bulunacak
    for i in coloums:
        boxes = np.vsplit(i,10) # dikey kesim gercekleştikten sonra ilk sutun için satır kesimi yapılıyor
        # box = cv.circle(boxes[0],(5,15),3,(255,0,0),-1)
        # box = cv.circle(boxes[0],(16,15),3,(255,0,0),-1)
        # box = cv.circle(boxes[0],(12,6),3,(255,0,0),-1)
        # box = cv.circle(boxes[0],(12,22),3,(255,0,0),-1)
        # cv.imshow("a",box)
        # cv.waitKey(0)
        # burada circle çizerek  kırpma adına değerleri buluyorum
        box = (boxes[0])[9:22,8:16] # kırpma işlemi yapılyıor
        # cv.imshow("a",box)
        # cv.waitKey(0)
        ind = 0
        max = cv.countNonZero(box) # siyah olmayan piksel sayısını maxa eşitledim
        # burada en buyuk siyah olmayan değer bulunuyor
        for j in range(1,10):
            box = (boxes[j])[9:22,8:16]
            # cv.imshow("a",box)
            # cv.waitKey(0)
            if max < cv.countNonZero(box): # eğerki siyah olmayan piksel sayısı max dan buyukse yeni max değeri o oluyor
                max=cv.countNonZero(box) # indisde ona eşitleniyor
                ind = j
                if max < 60:
                    ind = -1
        if max < 60: # düzgün karalanmayan sıkları bos yani yanlış olması adına siyah olmama sayısı eşiğini 60 ayarladım
            ind = -1 # eşiği gecemeyen değerler -1 oldu
        if ind != -1: # -1 olmayan değerler girdi
            no = (no*10) + ind
        # no 0 dan başladı ilk değer 5 olsun 0 = 0 * 10 + 5 den 5
        # yeni no = 5,ikinci gelen değer 6 olsun , 5 = 5*10 + 6 dan 56 
        # bu şekilde ögr no bulunuyor
    return no

#ögrnonul fonksıyonu ile aynı mantık
def findAnswer(answers):
    res = []
    for ans in answers:
        boxes= np.hsplit(ans,5)
        box = (boxes[0])[4:22,4:18]
        max = cv.countNonZero(box)
        ind = 0
        for i in range(1,5):
            box = (boxes[i])[4:22,4:18]
            if max < cv.countNonZero(box):
                max= cv.countNonZero(box)
                ind = i
                if max < 170:
                    ind = -1
        if max < 170:
                    ind = -1
        res.append(ind)
    return res

# KOD BURADAN BAŞLAR
askNo = int(input("kaç soru var : ")) # 40 soruluk optik oldugu için soru sayısı kullanıcıdan alınmalı
p = os.getcwd() #(os işleitm sistemi için bir api)bulundugum dızını gosterıyor
path = os.listdir( p + '/fotograflar/') #bulundugum dızınde kı fotograflara atlıyorum ve listeliyorum
writingFile =  open("result.csv","w",encoding='utf-8')  # csv dosyasına yazmak için onu açtım
cvppath = "cevapanahtari.png" # bulundugum dızındekı cevap anahtarı
cevapanahtari = cv.imread(cvppath) #(imread img okuma yapar) cevap anahtarı okunuyor
cevapanahtari = ut.preprocess(cevapanahtari)  # ut = utilty.py dosyasının kısaltılması oraya işaret eder.
ans = allanswer(cevapanahtari) # allanswer ile tum cevaplar için resimde kırpma işlemleri uygulanıyor
ans = findAnswer(ans) # cevaplar bulunuyor

# bu fonksiyonda ögrenci cevapları ve cevap anahtarındakı değgerler karsılastırılıyor
def getResult(answers):
    result = 0
    for i in range(0,askNo): 
        if answers[i] == ans[i]:
            answers[i] = "T" # excell de gösterilmek adına yeni deger True nun t si
            result +=  (100 / askNo) # 20 soru varsa her doğru cevap için 5 puan resulta eklenıyor
        else:
             answers[i] = "F" # excell de gösterilmek adına yeni deger false nun f si
    return result

# bu dongude tum fotograflar belirtilen diziden teker teker okunuyor ve sonuc excelle yazılıyor
for i in range(0,len(path)):
    imgs = cv.imread('./fotograflar/' + path[i]) # fotograflar dızınıdekı tum sırayla fotoları oku
    imgs = ut.preprocess(imgs) #fotgrafı biçimlendir
    answers = allanswer(imgs) # allanswer ile tum cevaplar için resimde kırpma işlemleri uygulanıyor
    answers = findAnswer(answers) # ögrencinin işaretlediği şıklar bulunuyor
    csvWriter = csv.writer(writingFile) #(csv excell yazmak için api) dosya belirtiliyo
    writingrow = [str(ogrnoBul(imgs)),str(getResult(answers)),answers[0:askNo]] # ogrno , sonuc, ve yapılan hatalar excel e yazılmak adına diziye alındı
    csvWriter.writerow(writingrow) # excele yazma işlmei gerçekleşti
           




