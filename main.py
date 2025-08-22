import requests
from typing import List, Dict, Tuple
def get_mexc_book_ticker() -> List[Dict]:
    url = "https://api.mexc.com/api/v3/ticker/bookTicker"
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Ошибка при получении данных: {e}")
        return []
def calculate_spread_percentage(bid_price: float, ask_price: float) -> float:
    if bid_price <= 0:
        return 0
    return ((ask_price - bid_price) / bid_price) * 100
def analyze_spreads(data: List[Dict]) -> List[Tuple[str, float, float, float, float]]:
    spreads = []
    skipped_count = 0
    for ticker in data:
        try:
            symbol = ticker.get('symbol', 'Unknown')
            bid_price_str = ticker.get('bidPrice')
            ask_price_str = ticker.get('askPrice')
            if bid_price_str is None or ask_price_str is None:
                skipped_count += 1
                continue
            if bid_price_str == '' or ask_price_str == '':
                skipped_count += 1
                continue
            bid_price = float(bid_price_str)
            ask_price = float(ask_price_str)
            if bid_price <= 0 or ask_price <= 0:
                skipped_count += 1
                continue
            if ask_price <= bid_price:
                skipped_count += 1
                continue
            spread_percentage = calculate_spread_percentage(bid_price, ask_price)
            spread_absolute = ask_price - bid_price
            spreads.append((symbol, bid_price, ask_price, spread_percentage, spread_absolute))
        except (ValueError, TypeError, KeyError) as e:
            print(f"Ошибка обработки данных для {symbol}: {e}")
            skipped_count += 1
            continue
    if skipped_count > 0:
        print(f"Пропущено {skipped_count} торговых пар с некорректными данными")
    return spreads
def get_top_spreads(spreads: List[Tuple[str, float, float, float, float]], top_n: int = 20) -> List[
    Tuple[str, float, float, float, float]]:
    # Сортируем по процентному разрыву в убывающем порядке
    sorted_spreads = sorted(spreads, key=lambda x: x[3], reverse=True)
    return sorted_spreads[:top_n]
def print_results(top_spreads: List[Tuple[str, float, float, float, float]]):
    print("=" * 80)
    print(f"{'СИМВОЛ':<15} {'БИД':<12} {'АСК':<12} {'РАЗРЫВ %':<12} {'РАЗРЫВ АБС':<12}")
    print("=" * 80)
    for i, (symbol, bid, ask, spread_pct, spread_abs) in enumerate(top_spreads, 1):
        print(f"{i:2d}. {symbol:<12} {bid:<12.8f} {ask:<12.8f} {spread_pct:<12.4f} {spread_abs:<12.8f}")
def main():
    print("Получение данных с API MEXC...")
    data = get_mexc_book_ticker()
    if not data:
        print("Не удалось получить данные с API")
        return
    print(f"Получено {len(data)} торговых пар")
    spreads = analyze_spreads(data)
    if not spreads:
        print("Не удалось проанализировать данные - все пары были пропущены")
        return
    print(f"Успешно проанализировано {len(spreads)} торговых пар")
    top_spreads = get_top_spreads(spreads, 20)
    print(f"\nТОП 20 ТОРГОВЫХ ПАР ПО РАЗРЫВУ СТАКАНА:")
    print_results(top_spreads)
    if spreads:
        all_spreads = [s[3] for s in spreads]
        avg_spread = sum(all_spreads) / len(all_spreads)
        max_spread = max(all_spreads)
        min_spread = min(all_spreads)
        print(f"\nСТАТИСТИКА:")
        print(f"Средний разрыв: {avg_spread:.4f}%")
        print(f"Максимальный разрыв: {max_spread:.4f}%")
        print(f"Минимальный разрыв: {min_spread:.4f}%")
        print(f"Количество валидных пар: {len(spreads)}")
if __name__ == "__main__":
    main()
