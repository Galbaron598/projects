# def same_sum(A,B):
#     if A is None or B is None:
#         return "None"
#     if sum(A) == sum (B):
#         return "OK"
    
#     sum_A = sum(A)
#     sum_B = sum(B)
    
#     for i in A:
#         for j in B: 
#             new_sum_A = sum_A - A[i] + B[j]
#             A[i] = new_sum_A + sum_A + B[j]
#             A[i] = sum_A - A[i] + B[j] + sum_A + B[j]
#             A[i] = sum_A  + B[j]
#             new_sum_B = sum_B + A[i] - B[j]
#             A[i] = - new_sum_B +sum_B - B[j]
#             if  new_sum_A == new_sum_B:
#                 return {A[i], B[j]}
#             else: 
#                 return "no"
            
    


# sum_A - A[i] + B[j] = sum_B + A[i] - B[j]


#     sum_A - sum_B = 2*A[i] -2*B[j]

        
  
    
# def merge(intervals):
#     if intervals is None:
#         return "nope!"
#     if intervals == []:
#         return "empty"
    
    
#     intervals.sort(key=lambda i: i[0])
    
#     output =[intervals[0]]
    
#     for start, end in intervals[1:]:
#         lastend = output[-1][1]
#         if lastend >= start:
#             finalEnd = max(lastend, end)
#             output[-1][1]= finalEnd
#         else:
#             output.append([start,end])
#     return output

# print(merge([[1,3],[2,6],[8,10],[15,18]]))


# def maxProfit(prices):
#     if prices is None:
#         return "oh no!"
#     if prices == []:
#         return "empty!"
    
#     left, right = 0,1
#     maxPrice=0
    
#     while right < len(prices):
#         if prices[left] < prices[right]:
#             # maxPrice= max(prices[right]-prices[left],maxPrice)
#             maxPrice += prices[right]-prices[left]
#         left +=1
#         right +=1
            
#     return maxPrice

# print(maxProfit([7,1,5,3,6,4])) 


# def maxProfitDP(prices):
#     if prices is None:
#         return "None!"
#     if prices == []:
#         return "empty!"
    
#     left, right = 0,1
    
   
#     helper =[0]*len(prices)
    
    
#     while right< len(prices):
#         if prices[left]< prices[right]:
#             helper[right] = max(helper[right], 2*prices[right] - prices[left])   
#             # maxPrice = max(maxPrice, helper[right])      
#         else:
#             left=right
#         right +=1
#     return helper[-1]

# print(maxProfitDP([7,1,5,3,6,4])) 

        

           
        



            

    

        
    
    
def anagrams(word1, word2):
    if word1 is None or word2 is None:
        return False
    
    if len(word1) != len(word2):
        return False
    
    word1Array = list(word1)
    # print(word1Array)
    word2helper = set(word2)
    
    for letter in word1Array:
        if letter not in word2helper:
            return False
        word2helper.remove(letter)
        
    return True

print(anagrams("silent", "listen"))



# def elements(arrayInput):
#     if arrayInput is None:
#         return "not exist"
    
    
#     totalSum = sum(arrayInput)
    
#     for i in range(len(arrayInput)):
#         for j in range(len(arrayInput[i:])):
#             if arrayInput[i] + arrayInput[j] == totalSum - (arrayInput[i] + arrayInput[j]):
#                 return [arrayInput[i],arrayInput[j]]
            
#     return "not exist"

# arrayInput[i] + arrayInput[j] == totalSum - (arrayInput[i] + arrayInput[j])

# 2*(arrayInput[i] + arrayInput[j]) = totalSum

# 2*(arrayInput[j]) = totalSum - 2*arrayInput[i]

# newSet = set(arrayInput)

# while num in arrayInput:
#     newNum = totalSum/2 - num
#     if newNum in newSet: 
#         return
    
    
#     let x=y=7 
#     console.log(x)
#     console.log(y)
    
#     i=0
    
#     for (var i = 0; i < 3; i++) {
#   setTimeout(function() {
#     console.log(i);
#   }, 1000);
# }
  
  
  
  
  
  
  
class Node:
    def __init__(self,val,next):
        self.val = val
        self.next = next
        
    #    1 -> 2 ->3 ->4  
        
def reverse(head):
    if head is None:
        return None
    
    node = head
    new_head = head
    
    while node: 
        new_head = node.next
        new_head.next = node
        node = node.next
    return new_head

        
        
        
        
    
    
    
        
        
  
  
  
  
  
    
        
        
        
         




