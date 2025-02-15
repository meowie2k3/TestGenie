
from ..Diagram.Block import Block, BlockType
from ..Diagram.Connection import Connection, ConnectionType
import os
import re

def ContainAnalyzer(diagram, block, visited = []):
    visited.append(block)
    currType = block.type
    
    # print("Current content: ", currContent)
    # print("Current type: ", currType)
    
    # keep analyze if type is file or class or abstract class
    if (currType == BlockType.FILE 
        or currType == BlockType.CLASS
        or currType == BlockType.ABSTRACT_CLASS
        ):
        content = block.getContentNoComment()
        # print(content)
        lines = content.split('\n')
        # if type is file, analyze classes and functions (standalone functions)
        # if type is class, analyze functions
        blocks = []
        # File analyzing
        if (currType == BlockType.FILE):
            # two cases: class and abstract class
            if 'class ' in content:
                # this file have class(es)
                isClassContent = False
                openedBracket = 0
                className = ''
                classContent = []
                # class or final class
                for line in lines:
                    if line.strip().startswith('class ') or line.strip().startswith('final class '):
                        # first line of class
                        # NOTE: there is no class inside class
                        # get class name
                        className = line.split('class ')[1].split('{')[0].strip()
                        # print(className)
                        isClassContent = True
                        classContent.append(line)
                    elif '}' in line and isClassContent:
                        # two cases: class end or function end
                        classContent.append(line)
                        if '{' in line:
                            continue
                        if openedBracket > 0:
                            openedBracket = openedBracket - 1
                        else: 
                            # class end
                            isClassContent = False
                            classContent = '\n'.join(classContent)
                            blocks.append(Block(className, classContent, BlockType.CLASS))
                            classContent = []
                    elif '{' in line and isClassContent:
                        openedBracket = openedBracket + 1
                        classContent.append(line)
                    elif isClassContent:
                        classContent.append(line)
                
                # abstract class
                if 'abstract class ' in content or 'abstract final class ' in content:
                    isAbstractClassContent = False
                    openedBracket = 0
                    className = ''
                    classContent = []
                    for line in lines:
                        if line.strip().startswith('abstract class ') or line.strip().startswith('abstract final class '):
                            # first line of class
                            # NOTE: there is no class inside class
                            # get class name
                            if line.strip().startswith('abstract class '):
                                
                                className = line.split('abstract class ')[1].split('{')[0].strip()
                            # Check if it's an abstract final class
                            if line.strip().startswith('abstract final class '):
                                className = line.split('abstract final class ')[1].split('{')[0].strip()
                            # print(className)
                            isAbstractClassContent = True
                            classContent.append(line)
                        elif '}' in line and isAbstractClassContent:
                            # two cases: class end or function end
                            classContent.append(line)
                            if '{' in line:
                                continue
                            if openedBracket > 0:
                                openedBracket = openedBracket - 1
                            else: 
                                # class end
                                isAbstractClassContent = False
                                classContent = '\n'.join(classContent)
                                blocks.append(Block(className, classContent, BlockType.ABSTRACT_CLASS))
                                classContent = []
                        elif '{' in line and isAbstractClassContent:
                            openedBracket = openedBracket + 1
                            classContent.append(line)
                        elif isAbstractClassContent:
                            classContent.append(line)
                            
            # enum
            if 'enum ' in content:
                # no {} in enum
                # maybe () in enum
                # once } is found, enum end
                isEnumContent = False
                enumName = ''
                enumContent = []
                for line in lines:
                    if line.strip().startswith('enum '):
                        # first line of enum
                        enumName = line.split('enum ')[1].split('{')[0].strip()
                        isEnumContent = True
                        enumContent.append(line)
                    elif '}' in line and isEnumContent:
                        enumContent.append(line)
                        isEnumContent = False
                        enumContent = '\n'.join(enumContent)
                        blocks.append(Block(enumName, enumContent, BlockType.ENUM))
                        # print(enumContent)
                    elif isEnumContent:
                        enumContent.append(line)
                
            # function
            # standalone function / GlobalVar only!
            # strat: get rid of all analyzed class and enum first
            leftoverContent = content
            for b in blocks:
                leftoverContent = leftoverContent.replace(b.content, '')
            # get rid of import line
            leftoverContent = '\n'.join([line for line in leftoverContent.split('\n') if not line.strip().startswith('import')])
            # remove empty lines
            leftoverContent = '\n'.join([line for line in leftoverContent.split('\n') if line.strip() != ''])
            print("========Leftover content========")
            print(block.name)
            print(leftoverContent)
            
            # two case of function: difined return type or not (dynamic)
            # variable must have a type
            # print("========Function and GlobalVar========")
            funcAndVarBlocks = extract_functions_and_globals(leftoverContent)
            blocks.extend(funcAndVarBlocks)
        
        # Class analyzing
        if (currType == BlockType.CLASS):
            # two cases: class function and class attribute
            content = block.getContentNoComment() # should be no difference between content and contentNoComment
            print(content)
            # classContentBlock = extract_class_content(content)
            # blocks.extend(classContentBlock)
            
        
        
        # blocks recursive
        for b in blocks:
            # print(b)
            # print(b.content)
            diagram.blocks.append(b)
            diagram.connections.append(Connection(block, b, ConnectionType.CONTAIN))
            ContainAnalyzer(diagram, b, visited=visited)
            
    # find connection connected to this block and not visited
    connectedBlocks = [c.tail for c in diagram.connections if c.head == block and c.tail not in visited]
    for b in connectedBlocks:
        ContainAnalyzer(diagram, b, visited=visited)    
    
    
def extract_functions_and_globals(dart_code):
    function_pattern = re.compile(r'^\s*([\w<>]+)\s+(\w+)\s*\(([^)]*)\)\s*\{', re.MULTILINE)
    global_var_pattern = re.compile(
        r'^\s*(final|const|var|[\w<>]+(?:<[^>]+>)?)\s+(\w+)\s*=\s*(\{.*?\}|[^;]+);',
        re.MULTILINE | re.DOTALL
    )

    blocks = []

    # Extract functions using a balanced bracket approach
    for match in function_pattern.finditer(dart_code):
        return_type, name, params = match.groups()
        signature = f"{return_type} {name}({params})"  # Full function signature
        start = match.start()
        
        # Extract the full function body by tracking brackets
        bracket_count = 0
        end = start
        while end < len(dart_code):
            if dart_code[end] == '{':
                bracket_count += 1
            elif dart_code[end] == '}':
                bracket_count -= 1
                if bracket_count == 0:
                    end = end + 2  # Include the closing bracket
                    break
            end += 1

        content = dart_code[start:end]#.strip()
        blocks.append(Block(signature, content, BlockType.FUNCTION))
        
    # get rid of all functions
    for b in blocks:
        dart_code = dart_code.replace(b.content, '')

   # Extract global variables
    for match in global_var_pattern.finditer(dart_code):
        full_line = match.group(0).strip()  # Capture the entire line including type and name
        var_type, name = match.groups()[:2]  # Extract type and name only
        signature = f"{var_type} {name}"  # Full variable declaration (type + name)
        blocks.append(Block(signature, full_line, BlockType.GLOBAL_VAR))

    return blocks

def extract_class_content(class_body):
    """ Extracts functions, constructors, and attributes from an already extracted class body. """

    # Regular expression patterns
    function_pattern = re.compile(
        r'^\s*(?:@override\s*)?([\w<>]+(?:<[^>]+>)?)\s+(\w+)\s*\(([^)]*)\)\s*\{', re.MULTILINE
    )
    constructor_pattern = re.compile(
        r'^\s*(\w+)\s*\(([^)]*)\)\s*\{', re.MULTILINE
    )
    attribute_pattern = re.compile(
        r'^\s*(final|var|const|[\w<>]+(?:<[^>]+>)?)\s+(\w+)\s*(=.*)?;', re.MULTILINE
    )

    blocks = []
    temp_class_body = class_body  # Temporary body to remove extracted elements

    # Step 1: Extract functions first
    function_contents = []
    for func_match in function_pattern.finditer(temp_class_body):
        return_type, func_name, params = func_match.groups()
        signature = f"{return_type} {func_name}({params})"
        func_start = func_match.start()

        # Find full function body
        bracket_count = 0
        func_end = func_start
        while func_end < len(temp_class_body):
            if temp_class_body[func_end] == '{':
                bracket_count += 1
            elif temp_class_body[func_end] == '}':
                bracket_count -= 1
                if bracket_count == 0:
                    func_end += 1
                    break
            func_end += 1

        func_content = temp_class_body[func_start:func_end].strip()
        function_contents.append((func_content, func_start, func_end))
        blocks.append(Block(signature, func_content, BlockType.CLASS_FUNCTION))

    # Remove extracted functions from temp_class_body
    for block in blocks:
        temp_class_body = temp_class_body.replace(block.content, '')

    print(temp_class_body)
    
    # Step 2: Extract constructors
    constructor_contents = []
    for constructor_match in constructor_pattern.finditer(temp_class_body):
        constructor_name, params = constructor_match.groups()
        signature = f"{constructor_name}({params})"
        constructor_start = constructor_match.start()

        # Find full constructor body
        bracket_count = 0
        constructor_end = constructor_start
        while constructor_end < len(temp_class_body):
            if temp_class_body[constructor_end] == '{':
                bracket_count += 1
            elif temp_class_body[constructor_end] == '}':
                bracket_count -= 1
                if bracket_count == 0:
                    constructor_end += 1
                    break
            constructor_end += 1

        constructor_content = temp_class_body[constructor_start:constructor_end].strip()
        constructor_contents.append((constructor_content, constructor_start, constructor_end))
        blocks.append(Block(signature, constructor_content, BlockType.CLASS_CONSTRUCTOR))

    # Remove extracted constructors from temp_class_body
    for constructor_content, start, end in sorted(constructor_contents, key=lambda x: x[1], reverse=True):
        temp_class_body = temp_class_body[:start] + temp_class_body[end:]

    # Step 3: Extract attributes from the modified class body
    for attr_match in attribute_pattern.finditer(temp_class_body):
        attr_type, attr_name, attr_value = attr_match.groups()
        signature = f"{attr_type} {attr_name}"
        attr_content = attr_match.group(0).strip()  # Capture full line
        blocks.append(Block(signature, attr_content, BlockType.CLASS_ATTRIBUTE))

    return blocks