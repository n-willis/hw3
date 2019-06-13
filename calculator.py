def readNumber(line, index):
  number = 0
  while index < len(line) and line[index].isdigit():
    number = number * 10 + int(line[index])
    index += 1
  if index < len(line) and line[index] == '.':
    index += 1
    keta = 0.1
    while index < len(line) and line[index].isdigit():
      number += int(line[index]) * keta
      keta /= 10
      index += 1
  token = {'type': 'NUMBER', 'number': number}
  return token, index


def readPlus(line, index):
  token = {'type': 'PLUS'}
  return token, index + 1


def readMinus(line, index):
  token = {'type': 'MINUS'}
  return token, index + 1


def readMult(line, index):
  token = {'type': 'MULTIPLY'}
  return token, index + 1


def readDiv(line, index):
  token = {'type': 'DIVIDE'}
  return token, index + 1


def readParentheses(line, index):
  init = index
  section = [0, 0]
  if line[index] == '(':
    token = {'type': 'START'}
    return token, index + 1
  else:
    token = {'type': 'END'}    
    return token, index + 1

  
def tokenize(line):
  tokens = []
  index = 0
  while index < len(line):
    if line[index].isdigit():
      (token, index) = readNumber(line, index)
    elif line[index] == '+':
      (token, index) = readPlus(line, index)
    elif line[index] == '-':
      (token, index) = readMinus(line, index)
    elif line[index] == '*':
      (token, index) = readMult(line, index)
    elif line[index] == '/':
      (token, index) = readDiv(line, index)
    elif line[index] == '(' or line[index] ==  ')':
      (token, index) = readParentheses(line, index)
    else:
      print('Invalid character found: ' + line[index])
      exit(1)
    tokens.append(token)
  return tokens

# Determine range of each pair of parentheses
def group(tokens, index):
  span = [0, 0]
  layer = 0
  span[0] = index
  index += 1
  while index < len(tokens):
    if tokens[index]['type'] == 'END' and layer == 0:
      break
    elif tokens[index]['type'] == 'START':
      layer += 1
    elif tokens[index]['type'] == 'END':
      layer -= 1
    index += 1
  span[1] = index
  tokens[span[0]]['span'] = span
  return span[0]

# Determine order of evaluation
def organize(tokens):
  order = []
  index = 0
  while index < len(tokens):
    if tokens[index]['type'] == 'START':
      if order and tokens[index]['span'][1] < tokens[order[-1]]['span'][1]:
        temp = order[-1]
        order[-1] = index
        order.append(temp)
      else:
        order.append(index)
    index += 1
  return order

# Evaluate for multiplication and division, return new set of tokens
def multDiv(tokens):
  newTokens = []
  index = 0
  newIndex = 0
  while index < len(tokens):
    if tokens[index]['type'] == 'MULTIPLY':
      newTokens[newIndex - 1]['number'] = newTokens[newIndex - 1]['number'] * tokens[index + 1]['number']
      index += 2
    elif tokens[index]['type'] == 'DIVIDE':
      newTokens[newIndex - 1]['number'] = newTokens[newIndex - 1]['number'] / tokens[index + 1]['number']
      index += 2
    else:
      newTokens.append(tokens[index])
      newIndex += 1
      index += 1
  return newTokens


def plusMinus(tokens):
  answer = 0
  tokens.insert(0, {'type': 'PLUS'}) # Insert a dummy '+' token
  index = 1
  while index < len(tokens):
    if tokens[index]['type'] == 'NUMBER':
      if tokens[index - 1]['type'] == 'PLUS':
        answer += tokens[index]['number']
      elif tokens[index - 1]['type'] == 'MINUS':
        answer -= tokens[index]['number']
      else:
        print('Invalid syntax')
        exit(1)
    index += 1
    token = {'type': 'NUMBER', 'number': answer}
  return token


def evaluate(tokens):
  index = 0
  while index < len(tokens):
    if tokens[index]['type'] == 'START':
      index = group(tokens, index)
    index += 1
  order = organize(tokens)
  # If there are parentheses, evaluate each section in order
  if order:
    for i in range(len(order)):
      section = []
      count = 0
      start = order[i]
      end = start + (tokens[order[i]]['span'][1] - tokens[order[i]]['span'][0])
      tokens.pop(order[i])
      count += 1
      for j in range(start, end):
        if tokens[start]['type'] == 'END':
          break
        else:
          section.append(tokens[start])
          tokens.pop(start)
          count += 1
      for k in range(i+1, len(order)):
        if order[k] > order[i]:
          order[k] -= count
        else:
          tokens[order[k]]['span'][1] -= count
      section = multDiv(section)
      tokens[start] = plusMinus(section)
    newTokens = multDiv(tokens)
    answer = plusMinus(newTokens)['number']
    return answer
  else:
    newTokens = multDiv(tokens)
    answer = plusMinus(newTokens)['number']
    return answer


def test(line):
  tokens = tokenize(line)
  actualAnswer = evaluate(tokens)
  expectedAnswer = eval(line)
  if abs(actualAnswer - expectedAnswer) < 1e-8:
    print("PASS! (%s = %f)" % (line, expectedAnswer))
  else:
    print("FAIL! (%s should be %f but was %f)" % (line, expectedAnswer, actualAnswer))


def runTest():
  print("==== Test started! ====")
  test("1")
  test("1+2")
  test("1.0+2")
  test("1.0-2")
  test("1.0+2.0")
  test("1.0-2.0")
  test("1.0+2.1-3")
  test("1*2")
  test("1.0*2")
  test("1.0/2")
  test("1.0*2.0")
  test("1.0/2.0")
  test("1.0*2.0/3")
  test("1.0+2-3.0*4/5.0")
  test("1.2+3.4*5-6/7.8")
  test("(1+2)")
  test("(1+2)*(3-4)")
  test("(1+3*5)/(4-2)")
  test("(1+3*5)/(4-2*(5+1))")
  test("(1.0+3.0*5)/(4-2.0*(5.0+1.0))")
  print("==== Test finished! ====\n")

runTest()

while True:
  print('> ', end="")
  line = input()
  tokens = tokenize(line)
  answer = evaluate(tokens)
  print("answer = %f\n" % answer)
