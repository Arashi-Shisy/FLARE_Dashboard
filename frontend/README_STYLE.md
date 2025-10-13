# CSS設計の刷新（FLOCSS + Utility）

本プロジェクトの CSS を「見通し・再利用・安全な拡張」を基準に全面整理しました。
エントリーポイントは `src/styles/main.css`（`main.js` で import 済み）です。

## ディレクトリ構成
- `src/styles/foundation/` …… 変数・ベース（色/余白/影/フォントなど）
- `src/styles/layout/` ………… レイアウト（コンテナ・グリッド・ナビ）
- `src/styles/object/component/` … 小さな再利用部品（ボタン/カード/フォーム）
- `src/styles/object/utility/` …… ユーティリティ（余白/フレックス/文言色等）
- `src/styles/object/project/` …… 画面固有（例：イベント/お知らせ/チャット）
- `src/styles/object/project/_project-legacy.css` …… 後方互換のため残置（段階的に削除）

## 命名規約
- **Block-Element-Modifier (BEM) 風**：例）`.event-card`（Block）/ `.event-card__title`（Element）/ `.event-card--danger`（Modifier）  
  ※今回は互換性優先のため、`event-card .event-title` など **段階的移行** を採用
- **ユーティリティは `u-` 接頭**：`.u-hint`, `.u-mt-2`, `.u-flex`, `.u-gap-2` など

## 主な変更点（互換マッピング）
- `hint` → **`u-hint`**（全体置換）
- インライン style の余白指定 → **`u-mt-* / u-mb-*`** へ移行（代表値のみ置換）
- ナビゲーションのインライン `display:flex; gap:.5rem` → **`u-flex u-gap-2`** へ
- `EventCard` の右側ボタン縦並びに **`.event-actions`** を付与

## ユーティリティ（抜粋）
- 余白：`.u-mt-{0,1,2,3,4,6,8}`, `.u-mb-{…}`（4px スケール）
- テキスト：`.u-hint`
- レイアウト：`.u-flex`, `.u-flex-col`, `.u-gap-{1..4}`, `.u-right`, `.u-stack-{sm,md,lg}`

## 使い方ガイド
- 新しい CSS は **`foundation → layout → component → utility → project`** の順に読み込まれます。
- 画面固有のスタイルは `object/project/xxx.css` に寄せ、再利用できるものは `component/` へ昇格させてください。
- 既存スタイルを削除する前に、画面差異が出ないか **E2E/目視** で確認してください。

---

### 移行の観点（チェックリスト）
- [ ] 新規クラスを追加する前に、ユーティリティや既存コンポーネントで代替できないか確認したか
- [ ] インライン style をユーティリティに置き換えたか
- [ ] ページ固有ルールが `project/` に閉じているか（グローバル汚染の回避）
- [ ] 変数（色/余白/影）を `foundation/_variables.css` のトークン経由にしたか