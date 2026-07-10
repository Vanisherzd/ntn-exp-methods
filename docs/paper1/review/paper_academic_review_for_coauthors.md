# 論文學術內容與故事線審查報告 (Co-authors Review Report)

本報告針對本篇論文的**敘事結構 (Narrative)**、**學術貢獻 (Contributions)**、**創新亮點 (Novelty)** 及**文獻引用 (References)** 進行深度學術審查，並提供具體的修改建議。本審查著重於內容的學術深度與故事邏輯，暫不考慮排版細節，以便您直接與共同作者（Co-authors）分享討論。

---

## 一、 故事線與敘事結構審查 (Narrative & Storytelling)

### 1. 現有故事線優勢
* **新穎的系統視角**：將傳統的物理層多普勒補償問題，重塑為「資源受限終端在軌道預測不確定性下的**端點控制問題 (Endpoint Control)**」。這個 Hook 非常成功，將單純的信號處理拉高到系統能耗與時序管理的層次。
* **誠實的反向論證 (Negative Result)**：論文非常坦率地揭示「在真實 Black Kite TLE 數據上，單純的機器學習殘差預測無法擊敗經典的 SGP4 物理基線」，並以此帶出「證據門檻（Evidence Gate）」的必要性。這種「負面結果 + 防禦性設計」的敘事在頂級通信會議（如 ICC）中非常具有說服力且引人入勝。

### 2. 敘事結構的缺漏與改進空間
* **Section V 與 Section VI 之間的邏輯斷層**：
  * **問題**：目前從 Section V（軟體模擬與 Footprint 評估）過渡到 Section VI（硬體 Conducted-IQ 實驗）非常突兀。Section VI 目前讀起來像是一個被強行塞入的硬體驗證，而不是故事的自然延伸。
  * **修改建議**：在 Section V 與 Section VI 之間增加一段承上啟下的過渡文字，將硬體實測重新包裝為「驗證發射端控制迴路硬體路徑可行性」的必要步驟。
  * **建議修改方向**：
    > *"To bridge the gap between software-derived control proxies and physical transceiver hardware, we must verify that the transmitter-side control decisions (specifically, shifting the carrier frequency and adjusting timing margins) can be executed deterministically by an off-the-shelf low-power modem without introducing RF artifacts."*

---

## 二、 學術貢獻與創新度評估 (Contributions & Novelty)

### 1. 創新度（Novelty）亮點分析
本論文的創新點並不在於提出了複雜的深度學習架構，而是在於：
1. **Bridge the Gap**：在「高度受限的物聯網終端」上，首次將分析物理模型（SGP4）與數據驅動的殘差學習，以一個**低複雜度、具備自我審查機制（Evidence Gate）**的控制策略結合。
2. **Joint Timing-Frequency Scaling Model**：提出一個直接將 TLE 軌道不確定性（Staleness）轉化為端點發射保護時間（Guard Time）與能耗開銷的量化公式。這為未來低軌衛星物聯網（LEO-IoT）的低功耗邊緣設計提供了新的理論支撐。

### 2. 貢獻描述（Contributions）的提升建議
* **問題**：目前的 Contribution 寫法過於「防禦性」（花了大量篇幅寫 "no packet, no OTA, no live-satellite"）。雖然誠實很重要，但應該先**正面強調工作價值**，再點出邊界限制。
* **修改建議**：
  1. 將 MCU 資源佔用與超低推論開銷（326 KB Flash, 1.07 mJ）直接列為第三點貢獻的一部分，強調其**可部署性（Deployability）**。
  2. 重新調整 Contribution 列表的語氣。例如：
     * *“We formulate a joint timing-frequency scaling proxy model that mathematically links TLE propagation staleness to energy consumption, enabling battery-powered nodes to optimize transmit margins dynamically.”*
     * *“We demonstrate a practical implementation with an MCU-class footprint, proving that evidence-gated control is computationally feasible for resource-constrained IoT nodes.”*

---

## 三、 文獻回顧與引用缺漏 (References & Literature Review)

目前文獻庫（`refs.bib`）中有大量極具價值的論文**完全沒有被內文引用**。補齊這些引用能大幅提升本論文的學術厚度與同行評議的專業度：

### 1. 低軌衛星物聯網與 LR-FHSS 系統容量限制 (增強背景)
* **遺漏引用**：`santana2024acrda` (ALOHA 衝突解決), `knop2024header` (信頭網絡編碼), `farhat2025probabilistic` (信頭複製概率分配)。
* **融入建議**：在 Introduction 第一段討論 LR-FHSS 對頻率偏移敏感性時引用。
  > *“...due to the narrow occupancy of LR-FHSS sub-carriers, uncompensated Doppler shifts significantly degrade the capacity of random access networks, even when employing advanced replication and contention resolution schemes [santana2024acrda, knop2024header, farhat2025probabilistic].”*

### 2. 物聯網終端能耗建模與評估 (支撐能耗公式)
* **遺漏引用**：`sanchez2024energy` (LR-FHSS 能耗分析與評估)。
* **融入建議**：在 Section III-B 的能耗公式（Eq. 9-10）旁引用，以佐證我們的能耗代理模型（Energy Proxy Model）與真實硬體功耗相符。
  > *“Our energy-per-successful-burst proxy aligns with established empirical energy models for LR-FHSS transceivers [sanchez2024energy] by modeling the active RX guard and TX airtime window...”*

### 3. 機器學習於軌道預測與殘差修正 (對比先前工作)
* **遺漏引用**：`peng2021fusion` (分析與機器學習軌道融合預測), `varey2024pinn` (物理資訊神經網路狀態估計), `caldas2024leo` (結合外部變數的 ML 軌道預測)。
* **融入建議**：在 Related Work 的第 (iv) 類（Orbit-learning）中引用，用以對比我們在「端點發射側（Endpoint-side）」進行輕量化修正的獨特性：
  > *“Existing machine learning approaches target high-precision orbit determination at the gateway or satellite level, using hybrid physics-ML models or physics-informed neural networks (PINNs) [peng2021fusion, varey2024pinn, caldas2024leo]. Unlike these computation-heavy frameworks, our approach addresses the resource-constrained endpoint's local control decision...”*

### 4. 硬體收發器架構與實測驗證 (支撐 Section VI)
* **遺漏引用**：`jung2025lrfhss` (OJVT 2025 最新發表的 LR-FHSS 收發器設計與硬體驗證)。
* **融入建議**：在 Section VI 開頭引入，說明我們的 Conducted-IQ 測試與當前最新的硬體驗證工作看齊。
  > *“Building upon recent hardware transceiver architectures for direct-to-satellite IoT [jung2025lrfhss], we verify the deterministic transmit path of our endpoint using...”*

---

## 四、 給共同作者的具體修改分工建議 (Action Items)

| 任務 (Task) | 負責章節 | 修改動機 | 具體寫法範例 |
|---|---|---|---|
| **融入 ML 軌道預測文獻** | Intro / Related Work | 展現對 2024-2025 年軌道 ML 研究（如 PINNs 和 Exogenous variables）的掌握。 | 引用 `varey2024pinn`, `caldas2024leo` |
| **融入 LR-FHSS 最新進展** | Intro / System Model | 強化為何 residual frequency offset 會導致系統崩潰，引用衝突避免的最新研究。 | 引用 `santana2024acrda`, `knop2024header` |
| **重塑 Section VI 的敘事** | Section VI (HW) | 消除硬體章節與軟體章節的割裂感，強調「控制迴路物理可行性」。 | 增加與 Section V 的邏輯承接段落 |
| **強化 Contribution 3 的描述** | Intro (Contributions) | 將低能耗與小Footprint提升為核心貢獻，增加吸引力。 | 突出 326 KB Flash / 1.07 mJ 的邊緣計算優勢 |
