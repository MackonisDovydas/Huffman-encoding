import time
import os
import sys
from bitstring import ConstBitStream
from heapq import heappush, heappop, heapify
from bitarray import bitarray


def readFile(file_name):
    binary_file = ConstBitStream(filename=file_name)
    return binary_file


def get_bits(binary_text, num_of_bytes):
    bites = []
    while binary_text.pos < len(binary_text) - int(num_of_bytes):
        bites.append(binary_text.read('bin:{0}'.format(num_of_bytes)))
    last_bits_count = len(binary_text) % int(num_of_bytes)
    if last_bits_count != 0:
        last_bits = binary_text.read('bin:{0}'.format(last_bits_count))
        zero_count = int(num_of_bytes) - last_bits_count
        last_bits = '0' * zero_count + last_bits
        bites.append(last_bits)
    else:
        last_bits = binary_text.read('bin:{0}'.format(int(num_of_bytes)))
        bites.append(last_bits)
    return bites


def frequency(bites):
    freqs = {}
    for bite in bites:
        if bite not in freqs.keys():
            freqs[bite] = 1
        else:
            freqs[bite] += 1
    return freqs


def huffmanTree(freqs):
    heap = [[fq, [sym, ""]] for sym, fq in freqs.items()]  # '' is for entering the huffman code later
    heapify(heap)  #paverciam sarasa medziu
    if len(heap) == 1:
       right = [[key for key in freqs.keys()][0], '0']
       left = []
       return right, left
    while len(heap) > 1:
        right = heappop(heap)  #pasiimam maziausia elementa
        left = heappop(heap)
        for pair in right[1:]:
            pair[1] = '0' + pair[1]  #pridedam nuli einant i desine
        for pair in left[1:]:
            pair[1] = '1' + pair[1]  #vienetas einantiems i kaire
        heappush(heap, [right[0] + left[0]] + right[1:] + left[1:])
    return right[1:], left[1:]


def convertToRequiredSize(number, size):
    binary = "{0:b}".format(number)
    binary_lenght = len(binary)
    if binary_lenght < size:
        temporary = size - binary_lenght
        binary = '0' * temporary + binary
    return binary


def printFile(encoded_text, right, left, file_name, num_of_bytes):
    with open(file_name + '_compressed_file_{0}.bin'.format(num_of_bytes), 'wb') as w:

        file_name_binary = [format(ord(i), 'b') for i in file_name]
        for index, byte in enumerate(file_name_binary):
            file_name_binary[index] = convertToRequiredSize(int(byte, base=2), 8)
        file_name_binary = ''.join(file_name_binary)

        file_name_lenght_binary = convertToRequiredSize(len(file_name_binary), 8)
        write_buffer = ConstBitStream(bin=file_name_lenght_binary)  # failo pavadinimo ilgis
        write_buffer.tofile(w)

        write_buffer = ConstBitStream(bin=file_name_binary)  # failo pavadinimas
        write_buffer.tofile(w)

        num_of_bytes_binary = convertToRequiredSize(int(num_of_bytes), 8)
        write_buffer = ConstBitStream(bin=num_of_bytes_binary)  # kokias bitu gabalais buvo nuskaitytas tekstas
        write_buffer.tofile(w)

        best_k_size = bestSize(int(num_of_bytes))

        left_table_lenght_binary = convertToRequiredSize(len(left), int(best_k_size))
        write_buffer = ConstBitStream(bin=left_table_lenght_binary)  # lenteles ilgis
        write_buffer.tofile(w)

        right_table_lenght_binary = convertToRequiredSize(len(right), int(best_k_size))
        write_buffer = ConstBitStream(bin=right_table_lenght_binary)  # lenteles ilgis
        write_buffer.tofile(w)

        for k, v in left:
            padded_k = k.zfill(best_k_size)
            write_buffer = ConstBitStream(bin=padded_k)  # zodis
            write_buffer.tofile(w)

            v_lenght_binary = convertToRequiredSize(len(v), 8)
            write_buffer = ConstBitStream(bin=v_lenght_binary)  # uzkodavimo ilgis
            write_buffer.tofile(w)

            best_v_size = bestSize(len(v))

            padded_v = v.zfill(best_v_size)
            write_buffer = ConstBitStream(bin=padded_v)  # uzkodavimas
            write_buffer.tofile(w)

        for k, v in right:
            padded_k = k.zfill(best_k_size)
            write_buffer = ConstBitStream(bin=padded_k)  # zodis
            write_buffer.tofile(w)

            v_lenght_binary = convertToRequiredSize(len(v), 8)
            write_buffer = ConstBitStream(bin=v_lenght_binary)  # uzkodavimo ilgis
            write_buffer.tofile(w)

            best_v_size = bestSize(len(v))

            padded_v = v.zfill(best_v_size)
            write_buffer = ConstBitStream(bin=padded_v)  # uzkodavimas
            write_buffer.tofile(w)

        text_lenght = len(encoded_text)  # teksto ilgis
        text_lenght_binary = convertToRequiredSize(text_lenght, 32)
        write_buffer = ConstBitStream(bin=text_lenght_binary)
        write_buffer.tofile(w)

        best_text_size = bestSize(len(encoded_text))
        padded_encoded_text = encoded_text.zfill(best_text_size)
        write_buffer = ConstBitStream(bin=padded_encoded_text)  # uzkoduotas tekstas
        write_buffer.tofile(w)


def degree_printFile(context_huffman_list, encoded_text, degree, file_name):
    with open(file_name + 'compressed_file_degree_{0}.bin'.format(degree), 'wb') as w:

        file_name_binary = [format(ord(i), 'b') for i in file_name]
        for index, byte in enumerate(file_name_binary):
            file_name_binary[index] = convertToRequiredSize(int(byte, base=2), 8)
        file_name_binary = ''.join(file_name_binary)

        file_name_lenght_binary = convertToRequiredSize(len(file_name_binary), 8)
        write_buffer = ConstBitStream(bin=file_name_lenght_binary)  # failo pavadinimo ilgis
        write_buffer.tofile(w)

        write_buffer = ConstBitStream(bin=file_name_binary)  # failo pavadinimas
        write_buffer.tofile(w)

        degree_binary = convertToRequiredSize(int(degree), 8)
        write_buffer = ConstBitStream(bin=degree_binary)  # kokias bitu gabalais buvo nuskaitytas tekstas
        write_buffer.tofile(w)

        context_huffman_list_binary = convertToRequiredSize(len(context_huffman_list), 16 * int(degree))
        write_buffer = ConstBitStream(bin=context_huffman_list_binary)
        write_buffer.tofile(w)

        for line in context_huffman_list:
            write_buffer = ConstBitStream(bin=line[0])
            write_buffer.tofile(w)
            if len(line[1]) == 2:
                if len(line[1][0]) != 2:
                    line[1] = [line[1]]
            list_lenght_binary = convertToRequiredSize(len(line[1]), 8)
            write_buffer = ConstBitStream(bin=list_lenght_binary)
            write_buffer.tofile(w)
            for [k, v] in line[1]:
                write_buffer = ConstBitStream(bin=k)  # zodis
                write_buffer.tofile(w)

                v_lenght_binary = convertToRequiredSize(len(v), 8)
                write_buffer = ConstBitStream(bin=v_lenght_binary)  # uzkodavimo ilgis
                write_buffer.tofile(w)

                best_v_size = bestSize(len(v))

                padded_v = v.zfill(best_v_size)
                write_buffer = ConstBitStream(bin=padded_v)  # uzkodavimas
                write_buffer.tofile(w)
        text_lenght = len(encoded_text)  # teksto ilgis
        text_lenght_binary = convertToRequiredSize(text_lenght, 32)
        write_buffer = ConstBitStream(bin=text_lenght_binary)
        write_buffer.tofile(w)

        best_text_size = bestSize(len(encoded_text))
        padded_encoded_text = encoded_text.zfill(best_text_size)
        write_buffer = ConstBitStream(bin=padded_encoded_text)  # uzkoduotas tekstas
        write_buffer.tofile(w)


def getBits(encoded_text, lenght):
    text = encoded_text[:lenght]
    encoded_text = encoded_text[lenght:]
    return encoded_text, str(text).replace("b'", "").replace("'", "")


def decodeText(encoded_text, left_table_dict, right_table_dict):
    text= []
    buffer = {}
    temp_buffer = {}
    index = 0
    isItFirst = True
    for bit in encoded_text:
        if isItFirst:
            if bit == '0':
               buffer = right_table_dict
            elif bit == '1':
               buffer = left_table_dict
            index +=1
            isItFirst = False
        else:
            for k, v in buffer.items():
                if v[index] == bit:
                   temp_buffer[k] = v
            buffer = temp_buffer
            temp_buffer = {}
            index += 1
        if len(buffer) == 1:
             text.append([key for key in buffer.keys()][0])
             isItFirst = True
             index = 0
    return text


def decodeFile(compressed_file_name):
    encoded_text = readFile(compressed_file_name)
    encoded_text = encoded_text.read('bin:{0}'.format(len(encoded_text)))

    encoded_text, file_name_lenght = getBits(encoded_text, 8)
    file_name_lenght = int(file_name_lenght, base=2)  # gaunam failo pavadinimo ilgi

    encoded_text, file_name = getBits(encoded_text, file_name_lenght)
    file_name = ''.join(
        [chr(int(file_name[i:i + 8], base=2)) for i in range(0, len(file_name), 8)])  # gaunam orig. failo pav.

    encoded_text, num_of_bytes = getBits(encoded_text, 8)
    num_of_bytes = int(num_of_bytes, base=2)

    k_size = bestSize(int(num_of_bytes))

    encoded_text, left_table_lenght = getBits(encoded_text, int(k_size))
    left_table_lenght = left_table_lenght.replace('0', '', k_size - num_of_bytes)
    left_table_lenght = int(left_table_lenght, base=2)  # lenteles ilgis

    encoded_text, right_table_lenght = getBits(encoded_text, int(k_size))
    right_table_lenght = right_table_lenght.replace('0', '', k_size - num_of_bytes)
    right_table_lenght = int(right_table_lenght, base=2)  # lenteles ilgis

    left_table_dict = {}
    right_table_dict = {}
    for line in range(left_table_lenght):
        encoded_text, temp_key = getBits(encoded_text, k_size)
        temp_key = temp_key.replace('0', '', k_size - num_of_bytes)  # zodis

        encoded_text, v_lenght = getBits(encoded_text, 8)
        v_lenght = int(v_lenght, base=2)  # uzkodavimo ilgis

        v_size = bestSize(v_lenght)

        encoded_text, temp_value = getBits(encoded_text, v_size)
        temp_value = temp_value.replace('0', '', v_size - v_lenght)  # uzkodavimas
        left_table_dict[temp_key] = temp_value  # I lentele

    for line in range(right_table_lenght):
        encoded_text, temp_key = getBits(encoded_text, k_size)
        temp_key = temp_key.replace('0', '', k_size - num_of_bytes)  # zodis

        encoded_text, v_lenght = getBits(encoded_text, 8)
        v_lenght = int(v_lenght, base=2)  # uzkodavimo ilgis

        v_size = bestSize(v_lenght)

        encoded_text, temp_value = getBits(encoded_text, v_size)
        temp_value = temp_value.replace('0', '', v_size - v_lenght)  # uzkodavimas
        right_table_dict[temp_key] = temp_value  # I lentele

    encoded_text, text_lenght = getBits(encoded_text, 32)
    text_lenght = int(text_lenght, base=2)  # teksto ilgis

    text_full_size = bestSize(text_lenght)

    encoded_text, encoded_text = getBits(encoded_text, text_full_size)  # uzkoduotas tekstas
    encoded_text = encoded_text.replace('0', '', text_full_size - text_lenght)

    bites = decodeText(encoded_text, left_table_dict, right_table_dict)  # atkoduojame
    text = ''.join(bites)
    with open(file_name, 'wb') as f:  # orig. teksta atgal i faila
        write_buffer = ConstBitStream(bin=text)
        write_buffer.tofile(f)


def degree_decodeFile(compressed_file_name):
    encoded_text = readFile(compressed_file_name)
    encoded_text = encoded_text.read('bin:{0}'.format(len(encoded_text)))

    encoded_text, file_name_lenght = getBits(encoded_text, 8)
    file_name_lenght = int(file_name_lenght, base=2)  # gaunam failo pavadinimo ilgi

    encoded_text, file_name = getBits(encoded_text, file_name_lenght)
    file_name = ''.join(
        [chr(int(file_name[i:i + 8], base=2)) for i in range(0, len(file_name), 8)])  # gaunam orig. failo pav.

    encoded_text, degree = getBits(encoded_text, 8)
    degree = int(degree, base=2)

    encoded_text, context_huffman_list_lenght = getBits(encoded_text, 16 * int(degree))
    context_huffman_list_lenght = int(context_huffman_list_lenght, base=2)  # lenteles ilgis

    context_huffman_list = []
    huffman_list = []
    for i in range(context_huffman_list_lenght):
        encoded_text, context = getBits(encoded_text, 8 * degree)
        encoded_text, list_lenght = getBits(encoded_text, 8)
        list_lenght = int(list_lenght, base=2)
        for j in range(list_lenght):
            encoded_text, bite = getBits(encoded_text, 8)

            encoded_text, v_lenght = getBits(encoded_text, 8)
            v_lenght = int(v_lenght, base=2)  # uzkodavimo ilgis

            v_size = bestSize(v_lenght)

            encoded_text, temp_value = getBits(encoded_text, v_size)
            temp_value = temp_value.replace('0', '', v_size - v_lenght)
            huffman_list.append([bite, temp_value])
        context_huffman_list.append([context, huffman_list])
        huffman_list = []

    encoded_text, text_lenght = getBits(encoded_text, 32)
    text_lenght = int(text_lenght, base=2)  # teksto ilgis

    text_full_size = bestSize(text_lenght)

    encoded_text, encoded_text = getBits(encoded_text, text_full_size)  # uzkoduotas tekstas
    encoded_text = encoded_text.replace('0', '', text_full_size - text_lenght)
    if int(degree) == 1:
        bites = degree_decodeText(context_huffman_list, encoded_text)  # atkoduojame
    else:
        bites = second_degree_burn_decodeText(context_huffman_list, encoded_text)
    text = ''.join(bites)
    # print(context_huffman_list)
    # print(text)
    with open(file_name, 'wb') as f:  # orig. teksta atgal i faila
        write_buffer = ConstBitStream(bin=text)
        write_buffer.tofile(f)


def degree_decodeText(context_huffman_list, encoded_text):
    context = context_huffman_list[0][0]
    huffman_list = []
    huffman_list_buffer = []
    bit_buffer = ''
    decoded_list = []
    first = True
    i = 20

    for bit in encoded_text:
        if bit_buffer == '':
          for line in context_huffman_list:
              if context == line[0]:
                huffman_list = line[1]
                break
          if len(huffman_list) == 2:
              if len(huffman_list[0]) != 2:
                huffman_list = [huffman_list]
        bit_buffer += bit
        for line in huffman_list:
            if len(line[1]) < len(bit_buffer):
                pass
            elif line[1][len(bit_buffer)-1] == bit:  #sitas visada suveikia  ==> amzinas ciklas ==> whyyyyy
                huffman_list_buffer.append(line)
        #print("bit {0}: bit_buffer {1}: huffman_list {2}: huffman_list_buffer {3}".format(bit, bit_buffer, huffman_list, huffman_list_buffer))
        if len(huffman_list_buffer) == 1 and len(huffman_list_buffer[0]) == 2:
              byte = huffman_list_buffer[0][0]
              huffman_list_buffer = []
              bit_buffer = ''
              context = byte
              decoded_list.append(byte)
        else:
            huffman_list = huffman_list_buffer
            huffman_list_buffer = []
    return decoded_list


def second_degree_burn_decodeText(context_huffman_list, encoded_text):
    context = context_huffman_list[0][0]
    huffman_list = []
    huffman_list_buffer = []
    bit_buffer = ''
    decoded_list = []
    first = True

    for bit in encoded_text:
        if bit_buffer == '':
          for line in context_huffman_list:
              if context == line[0]:
                huffman_list = line[1]
                break
          if len(huffman_list) == 2:
              if len(huffman_list[0]) != 2:
                huffman_list = [huffman_list]
        bit_buffer += bit
        for line in huffman_list:
            if len(line[1]) < len(bit_buffer):
                pass
            elif line[1][len(bit_buffer)-1] == bit:  #sitas visada suveikia  ==> amzinas ciklas ==> whyyyyy
                huffman_list_buffer.append(line)
        #print("bit {0}: bit_buffer {1}: huffman_list {2}: huffman_list_buffer {3}: context {4}".format(bit, bit_buffer, huffman_list, huffman_list_buffer, context))
        if len(huffman_list_buffer) == 1 and len(huffman_list_buffer[0]) == 2:
              if first:
                 decoded_list.append(context)
                 first = False
              byte = huffman_list_buffer[0][0]
              huffman_list_buffer = []
              bit_buffer = ''
              context = context[8:]
              context+= byte
              decoded_list.append(byte)
        else:
            huffman_list = huffman_list_buffer
            huffman_list_buffer = []
    return decoded_list


def bestSize(number):
    while True:
        if (number % 8 == 0):
            return number
        else:
            number += 1


def findContext(bites, degree):
    context_huffman_list = []
    isFirst = True
    nextIteration = False
    #temp_var = degree
    firstTimes = int(degree)
    context_table = []
    collection = []
    nextIsGood = False
    for i in range(len(bites)-1):
        context = ''.join(bites[i:i+degree]) #pasiimam konteksta
        for line in context_huffman_list:
            if line[0] == context: #jei jau toki konteksta turejom - praleidziam
               nextIteration = True
               break
        if nextIteration:
           nextIteration = False #jei atkeliavom iki sicia - tokio konteksto dar neturejom
           continue
        for bit in bites:
            if isFirst: #jei pirmasis kontekstas -
               context_table.append(bit)
               firstTimes -=1
               if firstTimes == 0:
                  isFirst = False
            if len(collection) < degree:
                collection.append(bit)
            elif len(collection) == degree:
                if context == ''.join(collection):
                   nextIsGood = True
                   collection.pop(0)
                else:
                   collection.pop(0)
                   collection.append(bit)
            elif len(collection) > degree:
                print("something is wrong")
            if nextIsGood:
                 context_table.append(bit)
                 collection.append(bit)
                 nextIsGood = False
        context_huffman_list.append([context, context_table])
        print(len(context_huffman_list))
        context_table = []
        collection = []
    return context_huffman_list


def degree_encode_text(context_huffman_list, bites):
    context_table = []
    last_bite = ''
    first = True
    encoded_text = ""
    for bite in bites:
      if first:
          first = False
          last_bite = bite
      for line in context_huffman_list:
          if last_bite == line[0]:
              context_table = line[1]
              break
      if context_table == []:
          print("1Gabrielė pasakė, kad šito negali būti! {0}:{1}".format(last_bite, line[0]))
      last_bite = bite
      encoded_text += encode_bite(bite, context_table)
      context_table = []
    return encoded_text


def second_degree_burn_encode_text(context_huffman_list, bites):
    context_table = []
    last_bite = []
    first = True
    second = True
    encoded_text = ""
    for bite in bites:
      if first:
          first = False
          last_bite.append(bite)
      elif second:
          second = False
          last_bite.append(bite)
          continue
      if not second and not first:
          for line in context_huffman_list:
              if ''.join(last_bite) == line[0]:
                  context_table = line[1]
                  break
          if context_table == []:
              print("1Gabrielė pasakė, kad šito negali būti! {0}:{1}".format(last_bite, line[0]))
          last_bite.pop(0)
          last_bite.append(bite)
          encoded_text += encode_bite(bite, context_table)
          context_table = []
    return encoded_text


def encode_bite(bite, huffman_list):
    if len(huffman_list) == 2:
        if len(huffman_list[0]) != 2:
           huffman_list = [huffman_list]
    for line in huffman_list:
        if bite == line[0]:
            return line[1]
    print("2Gabrielė pasakė, kad šito negali būti! {0}: {1}: {2}".format(bite, huffman_list, len(huffman_list)))


if __name__ == "__main__":

    sys.argv = ['huffman.py', 'data/wp2506797.jpg', '1', '1']
    start = time.time()
    file_name = sys.argv[1]  # Paduodam failo pavadinimą per argumentą
    degree = sys.argv[2]
    if int(degree) > 0:
        num_of_bytes = 8
    else:
        num_of_bytes = sys.argv[3]  # Paduodam nuskaitomu bitų kiekį per argumentą

    file_name_basename = os.path.basename(file_name)

    #nuskaitom faila, gaunam reikiamo dydzio bitus
    binary_text = readFile(file_name)
    bites = get_bits(binary_text, num_of_bytes)
    #print(context_huffman_list)
    #gaunam daznius ir huffmano lenteles
    if int(degree) == 0:
        freqs = frequency(bites)
        right, left = huffmanTree(freqs)
        encoded_text = ""
        huffman_list = right + left

        zero_first_zero_second_huffman_list = []
        zero_first_one_second_huffman_list = []
        one_first_zero_second_huffman_list = []
        one_first_one_second_huffman_list = []

        for code in huffman_list:
          if code[0][0] == '0' and code[0][1] == '0' :
              zero_first_zero_second_huffman_list.append(code)
          elif code[0][0] == '0' and code[0][1] == '1':
              zero_first_one_second_huffman_list.append(code)
          elif code[0][0] == '1' and code[0][1] == '0':
              one_first_zero_second_huffman_list.append(code)
          elif code[0][0] == '1' and code[0][1] == '1':
              one_first_one_second_huffman_list.append(code)

        for bite in bites:
            if bite[0] == '0' and bite[1] == '0' :
              huffman_list = zero_first_zero_second_huffman_list
            elif bite[0] == '0' and bite[1] == '1' :
              huffman_list = zero_first_one_second_huffman_list
            elif bite[0] == '1' and bite[1] == '0' :
              huffman_list = one_first_zero_second_huffman_list
            elif bite[0] == '1' and bite[1] == '1' :
              huffman_list = one_first_one_second_huffman_list
            for code in huffman_list:
              if code[0] == bite:
                  encoded_text += code[1]

        printFile(encoded_text, right, left, file_name_basename, num_of_bytes)
        end = time.time()
        print("saved")
        print("time: {0}".format(end - start))
    else:
      context_huffman_list = []
      context_huffman_list = findContext(bites, int(degree))
      for index, line in enumerate(context_huffman_list):
          if len(line[1]) == 1:
             context_huffman_list[index] = [line[0], [line[1][0], "0"]]
             continue
          if line[1] == []:
             context_huffman_list.pop(index)
          else:
            line[1] = frequency(line[1])
            right, left = huffmanTree(line[1])
            line[1] = right + left
      if int(degree) == 1:
          encoded_text = degree_encode_text(context_huffman_list, bites)
          degree_printFile(context_huffman_list, encoded_text, degree, file_name_basename)
          end = time.time()
          print("time: {0}".format(end - start))
          print("saved")
      elif int(degree) == 2:
          #print(context_huffman_list)
          encoded_text = second_degree_burn_encode_text(context_huffman_list, bites)
          degree_printFile(context_huffman_list, encoded_text, degree, file_name_basename)
          end = time.time()
          print("time: {0}".format(end - start))
          print("saved")

    if int(degree) == 0:
        compressed_file_name = file_name_basename + '_compressed_file_{0}.bin'.format(num_of_bytes)
        start = time.time()
        decodeFile(compressed_file_name)
        end = time.time()
        print("decoded")
        print("time: {0}".format(end - start))
    else:
        compressed_file_name = file_name_basename + 'compressed_file_degree_{0}.bin'.format(degree)
        start = time.time()
        degree_decodeFile(compressed_file_name)
        end = time.time()
        print("time: {0}".format(end - start))
        print("decoded")
