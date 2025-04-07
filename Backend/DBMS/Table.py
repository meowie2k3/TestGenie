
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
    
    def getUpdateSQL(self, values: dict, conditions: dict):
        sql = f'UPDATE {self.name} SET '
        for column in values:
            sql += f'{column} = \'{values[column]}\', '
        sql = sql[:-2] + ' WHERE '
        for column in conditions:
            sql += f'{column} = \'{conditions[column]}\' AND '
        sql = sql[:-4]
        return sql
    

if __name__ == '__main__':
    blockTable = Table(
                'Block',
                {
                    'id': 'INT AUTO_INCREMENT PRIMARY KEY',
                    'name': 'VARCHAR(255)',
                    'content': 'TEXT',
                    'prediction': 'TEXT',
                    'type': 'INT',
                    '': 'FOREIGN KEY (type) REFERENCES BlockType(id)'
                }
            )
    sql = blockTable.getUpdateSQL(
        values={
            'prediction': 'test',
        },
        conditions={
            'id': 1,
        }
    )
    print(sql)
    pass