#Rating Product & Sorting Reviews in Amazon

#########################################
#İş Problemi
#########################################
#E-ticaretteki en önemli problemlerden bir tanesi ürünlere satış sonrası verilen puanların doğru şekilde hesaplanmasıdır.
#Bu problemin çözümü e-ticaret sitesi için daha fazla müşteri memnuniyeti sağlamak,
#satıcılar için ürünün öne çıkması ve satın alanlar için sorunsuz bir alışveriş deneyimi demektir.
#Bir diğer problem ise ürünlere verilen yorumların doğru bir şekilde sıralanması olarak karşımıza çıkmaktadır.
#Yanıltıcı yorumların öne çıkması ürünün satışını doğrudan etkileyeceğinden dolayı hem maddi kayıp hem de müşteri kaybına neden olacaktır.
#Bu 2 temel problemin çözümünde e-ticaret sitesi ve satıcılar satışlarını arttırırken müşteriler ise satın alma yolculuğunu sorunsuz olarak tamamlayacaktır.

#########################################
#Veri Seti Hikayesi
#########################################
#Amazon ürün verilerini içeren bu veri seti ürün kategorileri ile çeşitli metadataları içermektedir.
#Elektronik kategorisindeki en fazla yorum alan ürünün kullanıcı puanları ve yorumları vardır.

#reviewerID: Kullanıcı ID’si
#asin: Ürün ID’si
#reviewerName: Kullanıcı Adı
#helpful: Faydalı değerlendirme derecesi
#reviewText: Değerlendirme
#overall: Ürün rating’i
#summary: Değerlendirme özeti
#unixReviewTime: Değerlendirme zamanı
#reviewTime: Değerlendirme zamanı Raw
#day_diff: Değerlendirmeden itibaren geçen gün sayısı
#helpful_yes: Değerlendirmenin faydalı bulunma sayısı
#total_vote: Değerlendirmeye verilen oy sayısı

import matplotlib.pyplot as plt
import pandas as pd
import math
import scipy.stats as st
pd.set_option("display.max_columns", None)
pd.set_option("display.max_rows", None)

pd.set_option("display.expand_frame_repr", False)
pd.set_option("display.float_format", lambda x: "%.5f" % x)

df = pd.read_csv("amazon_review.csv")

##################################################################################
#Average Rating’i güncel yorumlara göre hesapladım ve var olan average rating ile kıyasladım.
##################################################################################
df.head()
df["overall"].mean()

df["reviewTime"].dtype
df["reviewTime"] = pd.to_datetime(df["reviewTime"], dayfirst=True)
current_date = pd.to_datetime(str(df["reviewTime"].max()))
df["day_diff"] = (current_date - df["reviewTime"]).dt.days
df.head()
df["day_diff"].describe([0.2, 0.4, 0.6, 0.8])
df["day_diff"].quantile(0.2)
df["day_diff"].quantile(0.4)
df["day_diff"].quantile(0.6)
df["day_diff"].quantile(0.8)

df[df["day_diff"] == df["day_diff"].quantile(0.4)][["reviewerID", "reviewText", "day_diff"]]

#zaman bazlı ortalamaların blirlenmesi
def time_based_weighted_average(dataframe, w1=24, w2=22, w3=20, w4=18, w5=16):
    return dataframe.loc[dataframe["day_diff"] <= dataframe["day_diff"].quantile(0.2), "overall"].mean() * w1 / 100 + \
           dataframe.loc[(dataframe["day_diff"] > dataframe["day_diff"].quantile(0.2)) & (dataframe["day_diff"] <= dataframe["day_diff"].quantile(0.4)), "overall"].mean() * w2 / 100 + \
           dataframe.loc[(dataframe["day_diff"] > dataframe["day_diff"].quantile(0.4)) & (dataframe["day_diff"] <= dataframe["day_diff"].quantile(0.6)), "overall"].mean() * w3 / 100 + \
           dataframe.loc[(dataframe["day_diff"] > dataframe["day_diff"].quantile(0.6)) & (dataframe["day_diff"] <= dataframe["day_diff"].quantile(0.8)), "overall"].mean() * w4 / 100 + \
           dataframe.loc[(dataframe["day_diff"] > dataframe["day_diff"].quantile(0.8)), "overall"].mean() * w5 / 100


time_based_weighted_average(df)
#Hiçbir işlem yapmadan önce tüm veri setindeki ortalamaları aldığımızda ortalama 4.587589013224822 çıkmıştı.
#Burada gözlemlediğimiz üzere kullanıcıların yorumları yaptıkları tarihlere göre bir ağırlıklandırma yaptığımızda değişkenimiz 4.600026902863648 çıktı.


##################################################################################
#Ürün için ürün detay sayfasında görüntülenecek 20 review’i belirledim.
##################################################################################
df["helpful_no"] = df["total_vote"] - df["helpful_yes"]
df = df[["reviewerName", "overall", "summary", "helpful_yes", "helpful_no", "total_vote", "reviewTime"]]

def wilson_lower_bound(up, down, confidence=0.95):
    """
    Wilson Lower Bound Score Hesaplar

    -Bernoulli parametresip için hesaplanacak güven aralığının alt sınırı WLB skoru olarak kabul edilir.
    -Hesaplanacak skor ürün sıralaması için kullanılır.
    -Not:
    Eğer skorlar 1-5 arasındaysa 1-3 negatif, 4-5 pozitif olarak işaretlenir ve bernoulliye uygun hale getirilebilir.
    Bu beraberinde bazı problemleri de getirir. Bu sebeple bayesian average rating yapmak gerekir.

    :param up: int
    up count
    :param down: int
    down count
    :param confidence: float
    """

def score_up_down_diff(up, down):
    return up - down

def score_average_rating(up, down):
    if up + down == 0:
        return 0
    return up / (up + down)

#score_pos_neg_diff
df["score_pos_neg_diff"] = df.apply(lambda x: score_up_down_diff(x["helpful_yes"], x["helpful_no"]), axis=1)

#score_average_rating
df["score_average_rating"] = df.apply(lambda x: score_average_rating(x["helpful_yes"], x["helpful_no"]), axis=1)

#wilson_lower_bound
df["wilson_lower_bound"] = df.apply(lambda x: wilson_lower_bound(x["helpful_yes"], x["helpful_no"]), axis=1)

df.sort_values("wilson_lower_bound", ascending=False).head(20)



