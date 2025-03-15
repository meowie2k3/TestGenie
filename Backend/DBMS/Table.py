
class Table:
    def __init__(self, name: str, columns: dict):
        self.name = name
        self.columns = columns
        
        
    def getCreateSQL(self):
        sql = f'CREATE TABLE IF NOT EXISTS {self.name} ('
        for column in self.columns:
            sql += f'{column} {self.columns[column]}, '
        sql = sql[:-2] + ')'
        return sql
    
    def getSelectSQL(self, conditions: dict):
        sql = f'SELECT * FROM {self.name} WHERE '
        for column in conditions:
            sql += f"{column} = '{conditions[column]}' AND "
        sql = sql[:-5]
        return sql
    
    def getInsertSQL(self, values: dict):
        sql = f'INSERT INTO {self.name} ('
        for column in values:
            sql += f'{column}, '
        sql = sql[:-2] + ") VALUES ("
        for column in values:
            sql += f"'{values[column]}', "
        sql = sql[:-2] + ')'
        return sql