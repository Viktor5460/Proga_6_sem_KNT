#include "BoardGameBST.h"
#include "ProjectMapStorage.h"

#include <chrono>
#include <fstream>
#include <iomanip>
#include <iostream>
#include <random>
#include <cstdlib>
#include <string>
#include <vector>

struct BenchRow {
    int size;
    int repeats;
    double bstAvgUs;
    double mapAvgUs;
};

static void runCorrectnessChecks() {
    BoardGameBST bst;
    ProjectMapStorage mapStorage;

    const GameRecord g1{1, "Azul", 2, 40, 7.8};
    const GameRecord g2{2, "Root", 2, 90, 8.1};
    const GameRecord g3{3, "Codenames", 4, 30, 7.2};

    bst.insert(g1);
    bst.insert(g2);
    bst.insert(g3);

    mapStorage.insert(g1);
    mapStorage.insert(g2);
    mapStorage.insert(g3);

    const bool checksOk =
        bst.contains(7.8) && bst.contains(8.1) && bst.contains(7.2) &&
        mapStorage.contains(7.8) && mapStorage.contains(8.1) && mapStorage.contains(7.2);

    if (!checksOk) {
        std::cerr << "[ERROR] Correctness checks failed.\n";
        std::exit(1);
    }

    bst.erase(8.1);
    mapStorage.erase(8.1);
    if (bst.contains(8.1) || mapStorage.contains(8.1)) {
        std::cerr << "[ERROR] Erase checks failed.\n";
        std::exit(1);
    }

    std::cout << "[OK] Correctness checks passed for BST and std::map storage.\n";
}

static std::vector<GameRecord> makeDataset(int n, std::mt19937& rng) {
    std::uniform_real_distribution<double> ratingDist(1.0, 10.0);
    std::uniform_int_distribution<int> playersDist(1, 8);
    std::uniform_int_distribution<int> durationDist(15, 240);

    std::vector<GameRecord> data;
    data.reserve(static_cast<std::size_t>(n));

    for (int i = 0; i < n; ++i) {
        // Обеспечиваем уникальность ключа, чтобы не было перезаписи.
        const double rating = ratingDist(rng) + static_cast<double>(i) * 1e-6;
        data.push_back(GameRecord{i + 1, "Game_" + std::to_string(i + 1), playersDist(rng), durationDist(rng), rating});
    }

    return data;
}

template <typename Storage>
static double benchmarkInsertOneRun(const std::vector<GameRecord>& data) {
    Storage storage;

    const auto t1 = std::chrono::high_resolution_clock::now();
    for (const auto& game : data) {
        storage.insert(game);
    }
    const auto t2 = std::chrono::high_resolution_clock::now();

    const std::chrono::duration<double, std::micro> diff = t2 - t1;
    return diff.count();
}

static BenchRow benchmarkSize(int n, int repeats, std::mt19937& rng) {
    double bstTotalUs = 0.0;
    double mapTotalUs = 0.0;

    for (int i = 0; i < repeats; ++i) {
        auto data = makeDataset(n, rng);
        bstTotalUs += benchmarkInsertOneRun<BoardGameBST>(data);
        mapTotalUs += benchmarkInsertOneRun<ProjectMapStorage>(data);
    }

    return BenchRow{n, repeats, bstTotalUs / repeats, mapTotalUs / repeats};
}

static void saveCsv(const std::vector<BenchRow>& rows, const std::string& path) {
    std::ofstream out(path);
    out << "size,repeats,bst_avg_us,map_avg_us,bst_faster_than_map\n";

    for (const auto& row : rows) {
        const double ratio = (row.mapAvgUs > 0.0) ? (row.mapAvgUs / row.bstAvgUs) : 0.0;
        out << row.size << ','
            << row.repeats << ','
            << std::fixed << std::setprecision(3)
            << row.bstAvgUs << ','
            << row.mapAvgUs << ','
            << ratio << '\n';
    }
}

int main() {
    runCorrectnessChecks();

    std::mt19937 rng(20260515);

    const std::vector<int> sizes{10, 100, 1000, 10000};
    std::vector<BenchRow> rows;
    rows.reserve(sizes.size());

    std::cout << "Lab 9 benchmark: insertion performance\n";
    std::cout << "Comparison: custom BST vs std::map (project-like storage)\n\n";

    for (const int n : sizes) {
        const int repeats = (n <= 1000) ? 60 : 20;
        BenchRow row = benchmarkSize(n, repeats, rng);
        rows.push_back(row);

        std::cout << "N=" << std::setw(5) << row.size
                  << " | repeats=" << std::setw(2) << row.repeats
                  << " | BST avg(us)=" << std::setw(10) << std::fixed << std::setprecision(3) << row.bstAvgUs
                  << " | map avg(us)=" << std::setw(10) << row.mapAvgUs
                  << " | map/BST=" << std::setw(7) << (row.mapAvgUs / row.bstAvgUs)
                  << '\n';
    }

    saveCsv(rows, "results/benchmark_results.csv");

    std::cout << "\nSaved CSV: results/benchmark_results.csv\n";
    std::cout << "Done.\n";

    return 0;
}
