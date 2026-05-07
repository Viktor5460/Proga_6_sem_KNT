#pragma once

#include "GameRecord.h"

#include <algorithm>
#include <cstddef>
#include <memory>
#include <utility>
#include <vector>

class BoardGameBST {
public:
    BoardGameBST() = default;

    void insert(const GameRecord& game) {
        root_ = insertImpl(std::move(root_), game);
    }

    bool contains(double rating) const {
        return containsImpl(root_.get(), rating);
    }

    void erase(double rating) {
        root_ = eraseImpl(std::move(root_), rating);
    }

    std::size_t size() const {
        return sizeImpl(root_.get());
    }

    int height() const {
        return heightImpl(root_.get());
    }

    std::vector<GameRecord> inorder() const {
        std::vector<GameRecord> out;
        out.reserve(size());
        inorderImpl(root_.get(), out);
        return out;
    }

private:
    struct Node {
        GameRecord value;
        std::unique_ptr<Node> left;
        std::unique_ptr<Node> right;

        explicit Node(const GameRecord& v) : value(v) {}
    };

    std::unique_ptr<Node> root_;

    static std::unique_ptr<Node> insertImpl(std::unique_ptr<Node> node, const GameRecord& game) {
        if (!node) {
            return std::make_unique<Node>(game);
        }

        if (game.rating < node->value.rating) {
            node->left = insertImpl(std::move(node->left), game);
        } else if (game.rating > node->value.rating) {
            node->right = insertImpl(std::move(node->right), game);
        } else {
            node->value = game;
        }

        return node;
    }

    static bool containsImpl(const Node* node, double rating) {
        if (!node) {
            return false;
        }
        if (rating < node->value.rating) {
            return containsImpl(node->left.get(), rating);
        }
        if (rating > node->value.rating) {
            return containsImpl(node->right.get(), rating);
        }
        return true;
    }

    static const Node* minNode(const Node* node) {
        const Node* current = node;
        while (current && current->left) {
            current = current->left.get();
        }
        return current;
    }

    static std::unique_ptr<Node> eraseImpl(std::unique_ptr<Node> node, double rating) {
        if (!node) {
            return nullptr;
        }

        if (rating < node->value.rating) {
            node->left = eraseImpl(std::move(node->left), rating);
            return node;
        }
        if (rating > node->value.rating) {
            node->right = eraseImpl(std::move(node->right), rating);
            return node;
        }

        if (!node->left) {
            return std::move(node->right);
        }
        if (!node->right) {
            return std::move(node->left);
        }

        const Node* successor = minNode(node->right.get());
        node->value = successor->value;
        node->right = eraseImpl(std::move(node->right), successor->value.rating);
        return node;
    }

    static std::size_t sizeImpl(const Node* node) {
        if (!node) {
            return 0;
        }
        return 1 + sizeImpl(node->left.get()) + sizeImpl(node->right.get());
    }

    static int heightImpl(const Node* node) {
        if (!node) {
            return 0;
        }
        return 1 + std::max(heightImpl(node->left.get()), heightImpl(node->right.get()));
    }

    static void inorderImpl(const Node* node, std::vector<GameRecord>& out) {
        if (!node) {
            return;
        }
        inorderImpl(node->left.get(), out);
        out.push_back(node->value);
        inorderImpl(node->right.get(), out);
    }
};
