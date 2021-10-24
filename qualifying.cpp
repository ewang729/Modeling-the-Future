#include <algorithm>
#include <fstream>
#include <iostream>
#include <math.h>
#include <vector>

using namespace std;

const int N = 10000;

struct Loan {
    int n, d;
    string date;
    double term, price, amt, rate, score;
};

bool comp_price(const Loan& a, const Loan& b) {
    return a.price < b.price;
}

bool comp_amt(const Loan& a, const Loan& b) {
    return a.amt < b.amt;
}

double mean(vector<double>& v) {
    double sum = 0;
    for (double x : v) sum += x;
    return sum / v.size();
}

double deviation(vector<double>& v) {
    double m = mean(v);
    double var = 0;
    for (double x : v) var += (x - m) * (x - m);
    return sqrt(var / v.size());
}

double binom(int n, int m) {
    double res = 1;
    for (int i = n; i > n - m; i--) res *= i;
    for (int i = 1; i <= m; i++) res /= i;
    return res;
}

int main()
{
    ifstream fin("data.txt");

    double num_low = 0, num_high = 0;
    double sum_low = 0, sum_high = 0;
    double num_ratio = 0, sum_ratio = 0;
    vector<Loan> loans;
    vector<double> loan_delin;
    vector<double> below_620;
    vector<double> above_620;
    vector<double> ratio;
    for (int i = 0; i < N; i++) {
        Loan l;
        fin >> l.n >> l.date >> l.term >> l.price >> l.amt >> l.rate >> l.score >> l.d;
        loan_delin.push_back(l.d);
        if (l.score < 620) below_620.push_back(l.rate);
        else above_620.push_back(l.rate);
        if (l.term == 15) ratio.push_back(l.amt / l.price);
        loans.push_back(l);
    }
    double percent_delin = mean(loan_delin);
    cout.precision(15);
    cout << "Percent delinquent: " << percent_delin << endl;
    cout << "Rate below 620: " << mean(below_620) << endl;
    cout << "Rate above 620: " << mean(above_620) << endl;
    cout << "Amount to price for 15 year loans: " << mean(ratio) << endl;

    sort(loans.begin(), loans.end(), comp_price);
    double price_max, price_mean, price_deviation;
    cout << "Price minimum: " << loans[0].price << endl;
    cout << "Price maximum: " << (price_max = loans[N - 1].price) << endl;
    vector<double> prices;
    for (const Loan& l : loans) {
        prices.push_back(l.price);
    }
    cout << "Price mean: " << (price_mean = mean(prices)) << endl;
    cout << "Price standard deviation: " << (price_deviation = deviation(prices)) << endl;

    sort(loans.begin(), loans.end(), comp_amt);
    cout << "Amount minimum: " << loans[0].amt << endl;
    cout << "Amount maximum: " << loans[N - 1].amt << endl;
    vector<double> amts;
    for (const Loan& l : loans) {
        amts.push_back(l.amt);
    }
    cout << "Amount mean: " << mean(amts) << endl;
    cout << "Amount standard deviation: " << deviation(amts) << endl;

    cout << "Most expensive home is " << (price_max - price_mean) / price_deviation << " deviations above the mean" << endl;

    vector<double> below_600;
    for (const Loan l : loans) {
        if (l.score < 600) below_600.push_back(l.d);
    }
    cout << "Probability of delinquency below score 600: " << mean(below_600) << endl;

    double complement = 0;
    for (int i = 0; i < 5; i++) {
        complement += binom(100, i) * pow(percent_delin, i) * pow(1 - percent_delin, 100 - i);
    }
    cout << "Probability of at least 5 delinquencies: " << 1 - complement << endl;

    vector<double> over_80;
    for (const Loan l : loans) {
        if (l.amt > 0.8 * l.price) over_80.push_back(l.d);
    }
    cout << "Probability of delinquency over 80%: " << mean(over_80) << endl;

    vector<double> thirty, fifteen;
    for (const Loan l : loans) {
        if (l.term == 30) thirty.push_back(l.rate);
        else fifteen.push_back(l.rate);
    }
    cout << "Difference in mean interest rates: " << mean(thirty) - mean(fifteen) << endl;

    vector<double> fifteen_delin;
    for (const Loan l : loans) {
        if (l.term == 15) fifteen_delin.push_back(l.d);
    }
    cout << "No delinquincy in next 25 15 year loans: " << pow(1 - mean(fifteen_delin), 25) << endl;

    const int lb[4] = { 300, 620, 690, 720 };
    const int ub[4] = { 619, 689, 719, 850 };
    vector<vector<Loan> > loans_by_credit(4);
    for (const Loan l : loans) {
        if (l.score >= lb[3]) loans_by_credit[3].push_back(l);
        else if (l.score >= lb[2]) loans_by_credit[2].push_back(l);
        else if (l.score >= lb[1]) loans_by_credit[1].push_back(l);
        else loans_by_credit[0].push_back(l);
    }
    cout << endl;
    for (int i = 0; i < 4; i++) {
        cout << "Range: " << lb[i] << " - " << ub[i] << endl;
        vector<double> loan_price_ratio;
        int num_delinquent = 0;
        for (const Loan l : loans_by_credit[i]) {
            loan_price_ratio.push_back(l.amt / l.price);
            num_delinquent += l.d;
        }
        cout << "Mean loan/pp ratio: " << mean(loan_price_ratio) << endl;
        cout << "Deviation loan/pp ratio: " << deviation(loan_price_ratio) << endl;
        cout << "# Delinquent: " << num_delinquent << endl;
        cout << "% Delinquent: " << num_delinquent / ((double) loans_by_credit[i].size()) << endl;
    }

    return 0;
}
