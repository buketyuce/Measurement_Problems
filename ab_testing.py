#AB Testi ile Bidding Yöntemlerinin Dönüşümünün Karşılaştırılması

#######################################################################
#İş Problemi
#######################################################################
#Facebook kısa süre önce mevcut "maximum bidding" adı verilen  teklif verme türüne alternatif olarak yeni bir teklif türü olan "average bidding"’i tanıttı.
#Müşterilerimizden biri olan xyz, bu yeni özelliği test etmeye karar verdi ve
#average bidding'in maximum bidding'den daha fazla dönüşüm getirip getirmediğini anlamak için bir A/B testi yapmak istiyor.
#A/B testi 1 aydır devam ediyor ve xyz bu A/B testinin sonuçlarını analiz edilmesini istiyor.
# xyz için nihai başarı ölçütü Purchase'dır. Bu nedenle, istatistiksel testler için Purchase metriğine odaklanılmalıdır


#######################################################################
#Veri Seti Hikayesi
#######################################################################
#Bir firmanın web site bilgilerini içeren bu veri setinde kullanıcıların gördükleri ve tıkladıkları reklam sayıları gibi bilgilerin yanı sıra buradan gelen kazanç bilgileri yer almaktadır.
#Kontrol ve Test grubu olmak üzere iki ayrı veri seti vardır.
#Bu veri setleri ab_testing.xlsx excel’inin ayrı sayfalarında yer almaktadır.
#Kontrol grubuna Maximum Bidding, test grubuna Average Bidding uygulanmıştır.

#Impression: Reklam görüntüleme sayısı
#Click: Görüntülenen reklama tıklama sayısı
#Purchase: Tıklanan reklamlar sonrası satın alınan ürün sayısı
#Earning: Satın alınan ürünler sonrası elde edilen kazanç


#######################################################################
#Veriyi Hazırlama ve Analiz Etme
#######################################################################

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
from scipy.stats import shapiro, levene, ttest_ind

pd.set_option("display.max_columns", None)
pd.set_option("display.expand_frame_repr", False)
pd.set_option("display.float_format", lambda x: "%.5f" % x)

data_frame_control = pd.read_excel("AB_Testi/ab_testing.xlsx", sheet_name="Control Group")
data_frame_test = pd.read_excel("AB_Testi/ab_testing.xlsx", sheet_name="Test Group")

df_control = data_frame_control.copy()
df_test = data_frame_control.copy()


def check_df(dataframe, head=5):

    # boyut bilgisi
    print("################### Shape ###################")
    print(dataframe.shape)

    # tip bilgisi
    print("################### Types ###################")
    print(dataframe.dtypes)

    #Baştan gözlemleyelim
    print("################### Head ###################")
    print(dataframe.head(head))

    #Sondan gözlemleyelim
    print("################### Tail ###################")
    print(dataframe.tail(head))

    #Veri setinde herhangi bir eksik değer var mı bakalım
    print("################### NA ###################")
    print(dataframe.isnull().sum())

    #Sayısal değişkenlerin dağılımına bakalım
    print("################### Quantiles ###################")
    print(dataframe.describe([0, 0.05, 0.50, 0.95, 0.99, 1]).T)

check_df(df_control)
check_df(df_test)

df_control["group"] = "control"
df_test["group"] = "test"

df = pd.concat([df_control, df_test], axis=0, ignore_index=False)
df.head()


#######################################################################
#A/B Testinin Hipotezinin Tanımlanması
#######################################################################
#hipotezi tanımladım.
#H0 : M1 = M2 (Kontrol grubu ve test grubu satın alma ortalamaları arasında fark yoktur.)
#H1 : M1!= M2 (Kontrol grubu ve test grubu satın alma ortalamaları arasında fark vardır.)

df.groupby("group").agg({"Purchase": "mean"})

#######################################################################
#Hipotez Testinin Gerçekleştirilmesi
#######################################################################
#Hipotez testi yapılmadan önce varsayım kontrollerini yaptım.
#Bunlar Normallik Varsayımı ve Varyans Homojenliğidir.
#Kontrol ve test grubunun normallik varsayımına uyup uymadığını Purchase değişkeni üzerinden ayrı ayrı test ettim.

#Normallik Varsayımı:
#H0: Normal dağılım varsayımı sağlanmaktadır.
#H1: Normal dağılım varsayımı sağlanmamaktadır.

# p < 0.05 H0 RED
# P > 0.05 H0 REDDEDİLEMEZ

#Test sonucuna göre normallik varsayımı kontrol ve test grupları için sağlanıyor mu?

test_stat, pvalue = shapiro(df.loc[df["group"] == "control", "Purchase"])
print("Test Stat = %.4f, p-value = %.4f" % (test_stat, pvalue))
#p-value = 0.5891
#H0 reddedilemez. Control grubunun değerleri normal dağılım varsayımını sağlamaktadır.

test_stat, pvalue = shapiro(df.loc[df["group"] == "test", "Purchase"])
print("Test Stat = %.4f, p-value = %.4f" % (test_stat, pvalue))
#p-value = 0.1541
#H0 reddedilemez. Control grubunun değerleri normal dağılım varsayımını sağlamaktadır.

#Varyans Homojenliği
#H0: Varyanslar homojendir.
#H1: Varyanslar homojen Değildir.
#p < 0.05 H0 RED
#p > 0.05 H0 REDDEDİLEMEZ

test_stat, pvalue = levene(df.loc[df["group"] == "control", "Purchase"],
                           df.loc[df["group"] == "test", "Purchase"])
print("Test Stat = %.4f, p-value = %.4f" % (test_stat, pvalue))
#pvalue = 0.1083
#H0 REDDEDİLEMEZ. Control ve Test grubunun değerleri varyans homojenliği varsayımını sağlamaktadır.
#Varyanslar Homojendir.

#Varsayımlar sağlandığı için bağımsız iki örneklem t testi (parametrik test) yapılmaktadır.
# H0: M1 = M2 (Kontrol grubu ve test grubu satın alma ortalamaları arasında istatistiksel olarak anlamlı fark yoktur.
# H0: M1 != M2 (Kontrol grubu ve test grubu satın alma ortalamaları arasında istatistiksel olarak anlamlı fark vardır.
# p<0.05 H0 RED, p>0.05 H0 REDDEDİLEMEZ.

test_stat, pvalue = ttest_ind(df.loc[df["group"] == "control", "Purchase"],
                              df.loc[df["group"] == "test", "Purchase"],
                              equal_var=True)

print("Test Stat = %.4f, p-value = %.4f" % (test_stat, pvalue))

#p-value = 0.3493
# H0 reddedilemez. Kontrol grubu ve test grubu satın alma ortalamaları arasında istatistiksel olarak anlamlı fark yoktur.


#######################################################################
#Sonuçların Analizi
#######################################################################
# İlk önce iki gruba da normallik testi uygulanmıştır. İki grubunda normal dağılıma uyduğu gözlemlendiğinden
# İkinci varsayıma geçilerek varyansın homojenliği incelenmiştir. Varyanslar homojen çıktığından
# "Bağımsız" İki Örneklem T Testi uygulanmıştır. Uygulama sonucunda p-değerinin 0.05 ten büyük olduğu gözlenmiştir.
# ve H0 hipotezi reddedilememiştir.

#Tavsiyeler:
#Satın alma anlamında anlamlı bir fark olmadığından müşteri iki yöntemden birini seçebilir fakat burda diğer istatistiklerdeki
#farklılıklar da önem arz edecektir. Tıklanma, Etkişelim, Kazanç ve Dönüşüm Oranlarındaki farklılıklar değerlendirilip hangi
#yöntemin daha kazançlı olduğu tespit edilebilir. Özellikle Facebook'a tıklama başına para ödendiği için hangi yöntemde tıklanma
#oranın daha düşük olduğu tespit edilip ve CTR (Click Through Rate- Tıklama Oranı) oranına bakılabilir.
#iki grup gözlenmeye devam edilir.