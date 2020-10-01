#pragma once
#include <poly.h>
#include <string>


class CompiledPenalty{
public:
    string label;
    PolyBase* poly;

    CompiledPenalty(
        string label,
        PolyBase* poly
    ):
        label(label),
        poly(poly){}
};
