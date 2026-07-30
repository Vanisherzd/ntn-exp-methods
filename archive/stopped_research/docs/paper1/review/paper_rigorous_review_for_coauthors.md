# LEO-Hybrid-PGRL 論文深度學術評審意見 (Rigorous Peer-Review Critique)

本評審報告採用 IEEE ICC 審稿人（Reviewer）的嚴厲視角，針對當前版本 [icc_main.tex](file:///Users/laizhendong/Desktop/LEO-Hybrid-PGRL/paper/icc_main.tex) 的**學術邏輯缺陷**、**實驗設計漏洞**、**論證合理性**及**文獻支撐完整度**進行深度剖析。

---

## 總體評價 (Overall Executive Summary)

這篇論文試圖解決低軌衛星物聯網（LEO-IoT）中，由於雙軌根數（TLE）失效而導致的發射端多普勒頻偏與時間對齊補償問題。作者提出了一個名為「Evidence Gate」的機制，在真實數據上當機器學習無法擊敗 SGP4 物理模型時關閉學習，回退到物理基線；並在存在系統誤差的模擬場景下開啟學習。

然而，以當前版本的寫作與論證強度，投稿至 IEEE ICC Workshop 面臨極高的拒稿風險（High Rejection Risk）。論文存在多處**核心邏輯斷層**、**避重就輕的硬體論證**，以及**實驗設計的套套邏輯（Tautology）**。以下是審稿人視角的嚴厲批判與修改建議。

---

## 核心學術缺漏與嚴厲批評 (Critical Pitfalls & Critiques)

### 評審意見一：硬體驗證的「名實不符」與論證割裂 (Hardware Validation Disconnect)
* **嚴厲批評**：
  * Section VI（Preliminary Conducted-IQ Evidence）名義上是「硬體實測驗證」，但實際上它**根本沒有驗證論文提出的任何控制算法**。
  * 論文的算法核心是「利用 TLE 不確定性來動態調整守護時間、頻率邊限與發射功率」，然而 Section VI 的實測僅僅是在固定的 $923.2$ MHz 載波下，以最低功率發射信號，並確認 USRP 能抓到這個信號（+41 dB separation）。這個測試**沒有多普勒補償**，**沒有時序對齊**，甚至**沒有運行任何機器學習推論或 Evidence Gate**。
  * 這只是「發射端硬體能工作」的 Sanity Check，而不是對「控制算法」的驗證。此外，論文宣稱有 Conducted-IQ 實測，卻連一張**頻譜圖 (Spectrum/PSD Trace) 或是測試拓撲圖都沒有放出來**，僅憑 Table III 的幾個數字，極易讓審稿人懷疑實驗的真實性或完整度。
* **修改建議**：
  1. **必須引入圖表**：將 `paper/figures_final/fig_conducted_iq_evidence.pdf` 做為 **Figure 4** 放入 Section VI，至少證明我們有完整的測試路徑（Panel A）、數據矩陣（Panel B）和遮罩處理後的真實頻譜（Panel C）。
  2. **收斂硬體宣稱，強化邏輯承接**：在 Section VI 開頭老實承認：硬體實驗旨在「驗證發射端射頻前端在頻率微調與超低功耗發射時的硬體底座可行性」，而非演算法的 Closed-loop 驗證。

---

### 評審意見二：機器學習失敗的「套套邏輯」與 Evidence Gate 的虛無性 (Tautological ML Design)
* **嚴厲批評**：
  * 論文的 headline result 是「機器學習無法擊敗 SGP4（Table I）」，並以此作為提出 Evidence Gate 的動機。然而，審稿人會強烈質疑：**這是不是因為你們的 ML 特徵設計太差，或是數據處理不當？**
  * 真實的 TLE 更新（Space-Track 數據）反映的是軌道測定（Orbit Determination）的擬合噪聲、大氣阻力微調與觀測弧段差異。如果這些殘差在數學上接近零均值且無序（即白噪聲），那麼任何 ML 模型（Ridge, MLP）都**注定無法預測它**。
  * 如果殘差本質上就是不可預測的噪聲，那麼設計一個 Evidence Gate 來「關閉機器學習」就變成了套套邏輯——**你們自己設計了一個注定會失敗的機器學習實驗，然後再設計一個閘門來證明它被關閉了。** 這樣的論證在學術上缺乏深度。
* **修改建議**：
  1. **增加殘差的統計分析**：在 Section II-B 或 Section V 增加一段對真實殘差 $r(t)$ 的自相關性（Autocorrelation）與頻譜密度分析，證明真實 TLE 殘差的「不可預測性」是有物理與數學依據的（例如由於 Space-Track 擬合演算法的非線性截斷）。
  2. **重新包裝故事線**：不要把 Gate 寫成「拯救差勁 ML 的工具」，而要寫成「**防禦性控制策略 (Defensive Control Policy)**」——在物聯網節點上，發射失敗的能耗開銷極大，因此必須有「物理基線優先，僅在有實證時才啟用學習」的嚴苛門檻。

---

### 評審意見三：過度依賴「簡化代理指標」，缺乏通信物理層模擬 (Lack of PHY-Layer Realism)
* **嚴厲批評**：
  * 本文的所有控制效果評估（Fig. 3）都是基於「軟體代理指標（Proxies）」，例如將頻率誤差大於 500 Hz 直接定義為 Outage。
  * 這在通信領域是極不專業的簡化。真實的 LR-FHSS 接收機（如 Semtech 網關）在多普勒頻偏下，其封包誤碼率（PER）與信噪比（SNR）、頻率漂移率（Doppler Drift Rate）以及信頭（Header）的解碼成功率密切相關。單純用高斯分佈的尾部概率（Eq. 12）來代替 PER，會被審稿人指責為「數學遊戲」，缺乏真實通信信道模型（如 3GPP NTN 衛星信道）的支撐。
* **修改建議**：
  * 雖然 Workshop 篇幅有限，但必須在 Section III-C（Control Proxies）中，詳細說明 500 Hz 容差與 $3\sigma$ 守護時間是如何從 Semtech 官方技術白皮書（AN1200.64）或 3GPP 協議中推導出來的。
  * 在 Limitations 中更誠實、更嚴厲地指出：當前的能量與成功率估算均基於理想高斯信道下的幾何投影，未來工作需要導入標準 NTN 信道衰落模型。

---

## 參考文獻的嚴重缺失 (Bibliography Omissions)

目前 `refs.bib` 中有多篇 2024-2025 年的關鍵文獻被論文完全忽視。審稿人如果發現相關領域的重要進展未被提及，會直接給予 "Poor Literature Review" 的評價。

### 1. LR-FHSS 的系統容量與碰撞解決機制
* **應引用文獻**：`santana2024acrda` (IoTJ 2024), `knop2024header` (TVT 2024), `farhat2025probabilistic` (Access 2025)。
* **缺失後果**：論文在 Introduction 第一段提到多普勒頻偏導致的系統開銷時，沒有引用最新的 LR-FHSS 信頭優化與衝突解決機制，顯得研究背景停留在 2023 年以前。

### 2. 機器學習應用於軌道預測的最新對手
* **應引用文獻**：`varey2024pinn` (PINNs 應用於軌道估計), `caldas2024leo` (機器學習低軌軌道預測)。
* **缺失後果**：當前論文在 Related Work 僅引用了經典 SGP4，忽視了 2024 年最新的「物理資訊神經網路 (PINN)」在軌道預測上的應用。這會讓評審覺得我們對對手的設定（Baseline）過於過時。

### 3. 硬體收發器架構與實測對照
* **應引用文獻**：`jung2025lrfhss` (OJVT 2025 最新 LR-FHSS 硬體收發器驗證)。
* **缺失後果**：Section VI 缺乏對最新硬體實現的對照，無法突顯我們「發射端超低推論開銷（1.07 mJ）」的競爭優勢。

---

## 具體修改對照代碼建議 (LaTeX Modifications)

為了提升論文的通過率，以下修改**勢在必行**：

### Step 1: 補齊 Figure 4 (Conducted-IQ Evidence)
在 [icc_main.tex](file:///Users/laizhendong/Desktop/LEO-Hybrid-PGRL/paper/icc_main.tex) 第 622 行之後，Table III 之前，插入以下代碼：

```latex
\begin{figure}[!htbp]
    \centering
    \includegraphics[width=0.48\textwidth]{figures_final/fig_conducted_iq_evidence.pdf}
    \caption{Conducted IQ-level measurement-path verification. (A) Hardware routing topology and diagnostic protocol under a cabled 50~dB attenuated path with no antenna. (B) Verification matrix across multiple streaming rates and firmware configurations. (C) Masked max-hold spectrum trace confirming the target transmit-on signal peaks $\approx 41$~dB above the noise floor.}
    \label{fig:hw_evidence}
\end{figure}
```

### Step 2: 修正 Section V (現為 Section VI) 的段落描述
將 Section V 的開頭（第 612 行至 622 行）替換為以下更嚴謹、且包含限制邊界的文本：

```latex
A NUCLEO-L476RG $+$ Semtech LR1121 board (Board B) was flashed with a deterministic firmware fixed at 923.2~MHz and the lowest transmit power ($-17$~dBm, Low-Power PA), serial-verified (configured frequency/power, \texttt{TX\_START} $\to$ repeated LR-FHSS bursts $\to$ \texttt{TX\_DONE}). Over a conducted, 50~dB-attenuated coaxial path into a USRP~B210 (no antenna), the transmit-on capture shows an emission $\approx 41$~dB above the transmit-off noise floor ($41.25\pm0.36$~dB over four repeats; $43.76$~dB on a 2~MS/s control), peaking within the LR-FHSS hop grid, with no clipping or saturation; a waterfall of the window shows the hopping burst structure, and the per-burst peaks are reported as CFO / hop-center proxy candidates. A before/after reflash negative control isolates the earlier null to a board-side 868~MHz frequency mismatch. \textbf{This is conducted IQ-level measurement-path evidence of a controlled transmission only --- no packet decode, PER/PDR/CRC, gateway ACK, OTA, or live-satellite claim.}

Table~\ref{tab:hw} summarizes the conducted measurement-path sanity check. The corresponding diagnostic blocks, evidence matrix, and masked spectrum trace are visualized in Fig.~\ref{fig:hw_evidence}.
```
