
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
    
    def getSelectSQL(self,fields: list ,conditions: dict):
        # if conditions is empty, return all
        res = f'SELECT '
        if len(fields) == 0:
            res += '*'
        else:
            for field in fields:
                res += f'{field}, '
            res = res[:-2]
        res += f' FROM {self.name}'
        
        if len(conditions) > 0:
            res += ' WHERE '
            for condition in conditions:
                res += f"{condition} = '{conditions[condition]}' AND "
            res = res[:-4]
            
        return res
        pass
    
    def getInsertSQL(self, values: dict):
        sql = f'INSERT INTO {self.name} ('
        for column in values:
            sql += f'{column}, '
        sql = sql[:-2] + ") VALUES ("
        for column in values:
            sql += f"'{values[column]}', "
        sql = sql[:-2] + ')'
        return sql