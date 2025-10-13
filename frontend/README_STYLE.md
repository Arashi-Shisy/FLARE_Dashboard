# CSS 構成（FLOCSS に寄せた分割）

第一段階として、既存の `style.css` を `styles/object/project/_project-legacy.css` に移設し、
「壊さずに分割」を優先しています。今後は徐々にコンポーネント／ページ単位に切り出してください。

- `styles/foundation/` … 変数・ベース設定
- `styles/layout/` …… レイアウト層（将来のための空き枠）
- `styles/object/component/` … 小さな再利用部品（ボタン、カードなど）
- `styles/object/project/` … プロジェクト固有（現時点ではレガシー一式）
- `styles/object/utility/` … ユーティリティ（必要に応じて追加）

エントリーポイントは `src/styles/main.css` です（`main.js` で import 済み）。
