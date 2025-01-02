class StockUpdater:
    """
    Класс для обновления информации о запасах на основе ребер.
    """

    def __init__(self, stocks_by_city):
        self.stocks_by_city = stocks_by_city

    def update_from_edges(self, edges, stock, city_name):
        """
        Обновляет информацию о запасах на основе ребер.
        """
        for edge in edges:
            edge_city_from = edge.city_from.name_city
            edge_city_to = edge.city_to.name_city
            # Логика обновления для совпадающих городов
            if city_name == edge_city_to:
                if city_name == edge_city_from:
                    self.stocks_by_city[city_name] = {
                        "price": stock.price,
                        "quantity": stock.quantity,
                        "edge": True,
                        "transportation_cost": edge.transportation_cost,
                        "estimated_delivery_days": edge.estimated_delivery_days,
                    }
            else:
                self.stocks_by_city[edge_city_to] = {
                    "price": stock.price,
                    "quantity": stock.quantity,
                    "edge": True,
                    "transportation_cost": edge.transportation_cost,
                    "estimated_delivery_days": edge.estimated_delivery_days,
                }
