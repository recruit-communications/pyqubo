#pragma once
#include <iostream>


template<class T>
class LinkedList {
public:
    T value;
    LinkedList<T>* next = nullptr;
    LinkedList(T _value): value(_value){}
    LinkedList(T _value, LinkedList<T>* _next): value(_value), next(_next){}
    
    ~LinkedList(){
        if(next != nullptr){
            delete next;
        }
    }
};
