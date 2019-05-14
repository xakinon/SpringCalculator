import math, functools, itertools, operator

class SpringCalculate(object):
    def __init__(self, app=None, ui=None, conditions=None, Flist=None):
        self.headers = ['線径', '内径', '有効巻数', '自由高さ', '取付け高さ', '使用時高さ', '横弾性係数', 
                        '両端面研削の有無 0 = 無し 1 = 有り', 'コイル平均径', '総巻数', 'ばね指数', 
                        'ばね定数', 'ピッチ', '応力修正係数', '取り付け時ねじり修正応力',  '使用時ねじり修正応力', 
                        '密着高さ', '取り付け時荷重', '使用時荷重[N]', '縦横比', '動作範囲1', '動作範囲2', '使用時荷重[g]']
        self.conditions = conditions
        self.Flist = Flist
        self.ui = ui
        self.maxcount = 0
        self.app = app

    def uiUpdate(self, count):
        if self.ui is None or self.app is None:
            return
        self.ui.progressBar.setValue(count)
        self.ui.label.setText( str(count) + '/' + str(self.maxcount) )
        self.app.processEvents()

    def textSave(self, s, filename):
        with open(filename, 'a') as f:
            print(s, file=f)
        
    def calicurateCount(self):
        # 要素数を求めてラベルに表示
        c = [ list(c_) for c_ in self.conditions() ]
        maxcount = functools.reduce(operator.mul, map( len, [c[0], c[1], c[2], c[3], c[4], c[5], c[6], c[7]] ), 1)
        return maxcount

    def calicurate(self, filename):

        # ヘッダーを書き込み
        self.textSave( ', '.join( [ str(c) for c in self.headers ] ), filename )

        # 変数初期化
        count = 0
        str_buffer = ''
        c = self.conditions()
        self.maxcount = self.calicurateCount()

        for d, Di, Na, Hf, H1, H2, G, kensaku in itertools.product( c[0], c[1], c[2], c[3], c[4], c[5], c[6], c[7] ):
            try:

                count = count + 1

                if count % 2000 == 0:
                    self.uiUpdate(count)

                # 計算条件をspringに入れる
                spring = Spring(d, Di, Na, Hf, H1, H2, G, kensaku)

                # 条件確認
                if spring.checkCondition(self.Flist):
                    continue

                # springをリストに追加
                str_buffer = str_buffer + spring.toStr() + '\n'
                
                # 文字が10000を超えたらファイルに書き込み
                if len(str_buffer) > 10000:
                    self.textSave(str_buffer[:-1], filename)
                    str_buffer = ''

            except:
                pass

        self.textSave(str_buffer[:-1], filename)
        
class Spring(object):
    def __init__(self, d, Di, Na, Hf, H1, H2, G, kensaku):
        self.d  = d # 線径
        self.Di = Di # コイル内径
        self.Na = Na # 有効巻数
        self.Hf = Hf # 自由長さ
        self.H1 = H1 # 取り付け長さ
        self.H2 = H2 # 使用時長さ
        self.G  = G # 横弾性係数
        self.kensaku = kensaku # 切削
        
        # ばね関連の計算
        self.D   = round( Di + d, 6) # コイル平均径
        self.Nt  = round( Na + 2, 6) # 総巻数
        self.c   = round( self.D / d, 6) # ばね指数
        self.k   = round( G * (d**4) / (8 * Na * (self.D**3)), 6) # ばね定数
        self.P   = round( (Hf - (self.Nt - Na + 1 - kensaku) * d) / Na, 6) # ピッチ
        self.kt  = round( (4 * self.c - 1) / (4 * self.c - 4) + 0.615 / self.c, 6) # 応力修正係数
        self.Hs  = round( (self.Nt + 1 - kensaku) * d, 6) # 密着高さ
        self.F1  = round( self.k * (Hf - H1), 6) # 取り付け時荷重
        self.F2  = round( self.k * (Hf - H2), 6) # 使用時荷重
        self.Fg  = round( self.F2 / 9.8 * 1000, 6) # 使用時荷重[g]
        self.to1 = round( 8 * self.D * self.F1 / (math.pi * (d**3)), 6) # ねじり応力
        self.t1  = round( self.kt * self.to1, 6) # ねじり修正応力
        self.to2 = round( 8 * self.D * self.F2 / (math.pi * (d**3)), 6) # ねじり応力
        self.t2  = round( self.kt * self.to2, 6) # ねじり修正応力
        self.aspect     = round( Hf / self.D, 6) # 縦横比
        self.moveRange1 = round( (self.Hf - self.H1) / (self.Hf - self.Hs), 6) # 動作範囲1
        self.moveRange2 = round( (self.Hf - self.H2) / (self.Hf - self.Hs), 6) # 動作範囲2
        
    def checkCondition(self, Flist):
        # 動作範囲1が20%から80%か
        if self.moveRange1 < 0.2 or self.moveRange1 > 0.8:
            return True
            
        # 動作範囲2が20%から80%か
        if self.moveRange2 < 0.2 or self.moveRange2 > 0.8:
            return True

        # 荷重が負の場合スキップ
        if self.F1 <= 0 or self.F2 <= 0:
            return True
        
        # 取り付け高さ < 使用時高さの場合スキップ
        if self.H1 < self.H2:
            return True

        # ばね指数が4から22の範囲か
        if self.c < 4 or self.c > 22:
            return True

        # 縦横比が0.8から4の範囲か
        if self.aspect < 0.8 or self.aspect > 4:
            return True

        # ピッチが0.5D以下か
        if self.P > 0.5 * self.D:
            return True
        
        # 荷重が指定した値の±3%か
        f_frag = True
        for f in Flist:
            if self.Fg > f * 0.997 and self.Fg < f * 1.003:
                f_frag = False
        return f_frag

    def toStr(self):
        ls = [ self.d, self.Di, self.Na, self.Hf, self.H1, self.H2, self.G, self.kensaku,
               self.D, self.Nt, self.c, self.k, self.P, self.kt, self.t1, self.t2, self.Hs, 
               self.F1, self.F2, self.aspect, self.moveRange1, self.moveRange2, self.Fg]
        return ', '.join( [ str(c) for c in ls ] )
