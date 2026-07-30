# 論文修改意見與 LaTeX 修正對照表 (ICC Workshop 投稿準備)

本文件整理了針對 LEO-Hybrid-PGRL 論文 `paper/icc_main.tex` 的完整審查意見與 LaTeX 修改方案。這份意見旨在：
1. **補齊缺失的圖表 (Figure 4)** 以加強硬體實測的可信度。
2. **修正 Section V 的文字描述**，確保符合學術誠實邊界，避免評審質疑過度宣稱（Overclaiming）。
3. **最佳化排版與編譯警告**（解決雙欄對齊、間距最佳化以符合 6 頁上限）。

---

## 一、 量測圖表缺失與補齊建議 (Critical Omission)

### 1. 缺漏說明
目錄中已生成了高品質的硬體實測圖表 `paper/figures_final/fig_conducted_iq_evidence.pdf`（包含：A.量測拓撲與協議、B.驗證矩陣、C.經遮罩處理後的 PSD 頻譜軌跡），但目前 LaTeX 原始碼中完全沒有引入此圖表。

### 2. 修改方案
在 Section V (`Preliminary Conducted-IQ Evidence`) 中插入單欄寬度的 `\begin{figure}` 環境，並在內文中引用：

* **LaTeX 代碼插槽** (建議置於 Section V 開頭或 Table III 之前)：
```latex
\begin{figure}[!htbp]
    \centering
    \includegraphics[width=0.48\textwidth]{figures_final/fig_conducted_iq_evidence.pdf}
    \caption{Conducted IQ-level measurement-path verification. (A) Hardware routing topology and diagnostic protocol under a cabled 50~dB attenuated path with no antenna. (B) Verification matrix across multiple streaming rates and firmware configurations. (C) Masked max-hold spectrum trace confirming the target transmit-on signal peaks $\approx 41$~dB above the noise floor.}
    \label{fig:hw_evidence}
\end{figure}
```

---

## 二、 段落描述修正與邊界界定 (Honesty Guardrails)

### 1. 缺漏說明
目前的 Section V 文字描述過於簡略，未明確界定「有線實測（conducted IQ-level）」的學術限制，且缺少關鍵的對照組（Negative Control）描述。這容易被評審誤解為我們宣稱實現了「完整無線鏈路或封包解碼驗證」。

### 2. 修改方案
將 Section V（第 607 至 622 行）的文字，替換為符合安全審查規範的完整段落：

* **修改前 (Original)**：
```latex
Table~\ref{tab:hw} summarizes the conducted measurement-path sanity check.
NUCLEO-L476RG $+$ LR1121 board was reflashed to deterministic 923.2~MHz /
$-17$~dBm firmware and cabled through 50~dB attenuation into USRP~B210 RX2\,A
with no antenna. The reflash changed the 923~MHz capture from not visible under
stock 868~MHz firmware to a repeatable $41.25\pm0.36$~dB TX-ON/TX-OFF
separation, reproduced at 2~MS/s and after DC/LO artifact masking.
These observations verify the cabled IQ measurement path only; this 923.2~MHz
local AS923 run is separate from the 868~MHz software metrics and does not
exercise Doppler correction, evidence gating, packet decode, or over-the-air
behavior.
```

* **修改後 (Revised)**：
```latex
A NUCLEO-L476RG $+$ Semtech LR1121 board (Board B) was flashed with a deterministic firmware fixed at 923.2~MHz and the lowest transmit power ($-17$~dBm, Low-Power PA), serial-verified (configured frequency/power, \texttt{TX\_START} $\to$ repeated LR-FHSS bursts $\to$ \texttt{TX\_DONE}). Over a conducted, 50~dB-attenuated coaxial path into a USRP~B210 (no antenna), the transmit-on capture shows an emission $\approx 41$~dB above the transmit-off noise floor ($41.25\pm0.36$~dB over four repeats; $43.76$~dB on a 2~MS/s control), peaking within the LR-FHSS hop grid, with no clipping or saturation; a waterfall of the window shows the hopping burst structure, and the per-burst peaks are reported as CFO / hop-center proxy candidates. A before/after reflash negative control isolates the earlier null to a board-side 868~MHz frequency mismatch. \textbf{This is conducted IQ-level measurement-path evidence of a controlled transmission only --- no packet decode, PER/PDR/CRC, gateway ACK, OTA, or live-satellite claim.}

Table~\ref{tab:hw} summarizes the conducted measurement-path sanity check. The corresponding diagnostic blocks, evidence matrix, and masked spectrum trace are visualized in Fig.~\ref{fig:hw_evidence}.
```

---

## 三、 排版美化與雙欄平衡 (Formatting)

### 1. 最後一頁參考文獻雙欄對齊 (Column Equalization)
IEEE 格式要求論文最後一頁的兩欄長度需儘可能對稱平分。
* **修改方案**：
  1. 在 LaTeX 導言區（Preamble）引入 `balance` 巨集包：
     ```latex
     \usepackage{balance}
     ```
  2. 在文末 References 前（約第 683 行）插入 `\balance` 指令：
     ```latex
     \balance
     \bibliographystyle{IEEEtran}
     \bibliography{refs}
     ```

### 2. 字型警告解決建議 (Font Warnings)
目前編譯日誌中含有大量的 `Font shape undefined` 警告。
* **原因**：XeLaTeX 在無配置的情況下直接套用 IEEEtran 的 Times 字型，導致 Unicode 映射失敗。
* **修改方案**：建議投稿時改以 **pdfLaTeX** 進行編譯，或在導言區載入 `\usepackage{fontspec}` 並配置 Times New Roman，即可消除所有字型警告。

---

## 四、 版面空間微調 (Page Budget Control)

為了確保在加入 Figure 4 後，總頁數仍嚴格控制在 **6 頁**限制內，建議調整 Preamble 的垂直間距參數（第 15 至 21 行）：

* **修改前 (Original)**：
```latex
\setlength{\textfloatsep}{7pt plus 2pt minus 2pt}
\setlength{\dbltextfloatsep}{8pt plus 2pt minus 2pt}
\setlength{\floatsep}{7pt plus 2pt minus 2pt}
\setlength{\intextsep}{7pt plus 2pt minus 2pt}
\setlength{\abovedisplayskip}{4pt plus 1pt minus 1pt}
\setlength{\belowdisplayskip}{4pt plus 1pt minus 1pt}
```

* **修改後 (Revised)**：
```latex
\setlength{\textfloatsep}{6pt plus 1pt minus 1pt}
\setlength{\dbltextfloatsep}{7pt plus 1pt minus 1pt}
\setlength{\floatsep}{6pt plus 1pt minus 1pt}
\setlength{\intextsep}{6pt plus 1pt minus 1pt}
\setlength{\abovedisplayskip}{3pt plus 1pt minus 1pt}
\setlength{\belowdisplayskip}{3pt plus 1pt minus 1pt}
```
*(備註：若仍有些微溢出至第 7 頁，可微調文末的參考文獻間距 `\setlength{\itemsep}{0.5pt}`。)*
