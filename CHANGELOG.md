# Changelog

このプロジェクトにおける主な変更を記録します。形式は [Keep a Changelog](https://keepachangelog.com/ja/1.1.0/) を参考にし、バージョン番号は [PEP 440](https://peps.python.org/pep-0440/) に従います。

## Unreleased

## 0.2.0 - 2026-11-21

### Breaking Changes

- `Result[T, E]` / `Err[E]` から `E` の `bound=Exception` 制約を削除しました。`Err` は例外だけでなく、データクラス、Enum、文字列などの任意のエラー値を保持できます。`E` のデフォルトは引き続き `Exception` です。
- `Err.unwrap()` は元のエラーを直接送出せず、`UnwrapError` を送出するようになりました。`Err.expect()` も `RuntimeError` ではなく `UnwrapError` を送出します。元の値は `UnwrapError.error` から取得でき、`BaseException` の場合は `__cause__` にも設定されます。
- `combine_all()` が返す `Err` のエラー値は `ExceptionGroup` から `tuple[E, ...]` に変更されました。成功時の型は従来どおりです。

### Added

- `UnwrapError` を公開 API に追加。
- mypy を CI の型チェックに追加。
- 脆弱性報告と行動規範の公開方針を追加。

### Changed

- README の対象範囲、型安全性、`AwaitableResult` の単一消費制約を明確化。
- 公開 URL を `shimae-net/flow-res` に統一。

#### 0.2.0 への移行

- `unwrap()` / `expect()` の失敗を `except SomeError:` で捕捉していた場合は `except UnwrapError as exc:` に変更し、必要に応じて `exc.error`（または `exc.__cause__`）を検査してください。
- `combine_all()` の結果は `for error in errors:` のようにタプルとして反復してください。`errors.exceptions` は利用できません。
- `ExceptionGroup` を前提とした `except*` や `.exceptions` へのアクセスは、`UnwrapError` と `tuple[E, ...]` を扱うコードへ置き換えてください。

## 0.1.2 - 2026-07-28

- Python 3.13 向けの公開版。
