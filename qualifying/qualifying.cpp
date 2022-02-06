#include <algorithm>
#include <fstream>
#include <iostream>
#include <math.h>
#include <vector>

using namespace std;

const int N = 10000; //number of data points

//structure to represent a single loan
struct Loan {
    int n, d; //record number, delinquincy status
    int month, day, year;
    double term, price, amt, rate, score;
};

//comparator for comparing loans by price
bool comp_price(const Loan& a, const Loan& b) {
    return a.price < b.price;
}

//comparator for comparing loans by amount
bool comp_amt(const Loan& a, const Loan& b) {
    return a.amt < b.amt;
}

//function to find the arithmetic mean of a list
double mean(vector<double>& v) {
    double sum = 0;
    for (double x : v) sum += x;
    return sum / v.size();
}

//function to find the standard deviation of a list
double deviation(vector<double>& v) {
    double m = mean(v);
    double var = 0;
    for (double x : v) var += (x - m) * (x - m);
    return sqrt(var / v.size());
}

//function to calculate binomial coefficients (n choose m)
double binom(int n, int m) {
    double res = 1;
    for (int i = n; i > n - m; i--) res *= i;
    for (int i = 1; i <= m; i++) res /= i;
    return res;
}

int main()
{
    /*data was converted to text file
    * format is record number / month / day / year / term /
        purchase price / loan amount / credit score / delinquency
    */
    ifstream fin("data.txt"); //open data file
    cout.precision(10); //set precision of output

    vector<Loan> loans; //array containing all loans
    for (int i = 0; i < N; i++) {
        Loan l;
        fin >> l.n >> l.month >> l.day >> l.year >> l.term; //read in loan information
        fin >> l.price >> l.amt >> l.rate >> l.score >> l.d;
        loans.push_back(l);
    }

    /**PART 3 - Mathematical Modeling**/

    //question 7
    vector<double> loan_delin; //array containing delinquency of each loan
    for (const Loan& l : loans) {
        loan_delin.push_back(l.d);
    }
    double delin_rate = mean(loan_delin); //compute rate of delinquency
    cout << "Percent delinquent: " << delin_rate * 100 << endl;

    //question 8
    vector<double> rates_below_620;
    vector<double> rates_above_620;
    for (const Loan& l : loans) {
        if (l.score < 620) //split loans based on credit score
            rates_below_620.push_back(l.rate);
        else
            rates_above_620.push_back(l.rate);
    }
    cout << "Rate with score below 620: " << mean(rates_below_620) << endl;
    cout << "Rate with score above 620: " << mean(rates_above_620) << endl;

    //question 9
    vector<double> ratio_15;
    for (const Loan& l : loans) {
        if (l.term == 15)
            ratio_15.push_back(l.amt / l.price);
    }
    cout << "Loan to price for 15 year loans: " << mean(ratio_15) << endl;

    //question 10
    sort(loans.begin(), loans.end(), comp_price); //sort loans by purchase price
    double price_max, price_mean, price_deviation;
    cout << "Price minimum: " << loans[0].price << endl;
    cout << "Price maximum: " << (price_max = loans[N - 1].price) << endl;
    vector<double> prices;
    for (const Loan& l : loans) {
        prices.push_back(l.price);
    }
    cout << "Price mean: " << (price_mean = mean(prices)) << endl;
    cout << "Price standard deviation: " << (price_deviation = deviation(prices)) << endl;

    sort(loans.begin(), loans.end(), comp_amt); //sort loans by loan amount
    cout << "Amount minimum: " << loans[0].amt << endl;
    cout << "Amount maximum: " << loans[N - 1].amt << endl;
    vector<double> amts;
    for (const Loan& l : loans) {
        amts.push_back(l.amt);
    }
    cout << "Amount mean: " << mean(amts) << endl;
    cout << "Amount standard deviation: " << deviation(amts) << endl;

    //quesiton 11
    cout << "Most expensive home is " << (price_max - price_mean) / price_deviation << " deviations above the mean" << endl;

    //question 12
    vector<double> delin_below_600;
    for (const Loan& l : loans) {
        if (l.score < 600)
              delin_below_600.push_back(l.d);
    }
    cout << "Probability of delinquency with score below 600: " << mean(delin_below_600) << endl;

    //question 13
    double complement = 0; //compute the probability that less than 5 will be delinquent
    for (int i = 0; i < 5; i++) {
        //split into cases based on how many loans are delinquent
        complement += binom(100, i) * pow(delin_rate, i) * pow(1 - delin_rate, 100 - i);
    }
    cout << "Probability of at least 5 delinquencies in next 100 loans: " << 1 - complement << endl;

    //quesiton 14
    vector<double> delin_over_80;
    for (const Loan& l : loans) {
        if (l.amt > 0.8 * l.price)
            delin_over_80.push_back(l.d);
    }
    cout << "Probability of delinquency with amount more than 80% of price: " << mean(delin_over_80) << endl;

    //question 15
    vector<double> thirty_rate, fifteen_rate;
    for (const Loan& l : loans) {
        if (l.term == 30) //split based on term
            thirty_rate.push_back(l.rate);
        else
            fifteen_rate.push_back(l.rate);
    }
    cout << "Difference in mean interest rates: " << mean(thirty_rate) - mean(fifteen_rate) << endl;

    //question 16
    double expected = delin_rate * (-164563) + (1 - delin_rate) * (152946); //cases depending on delinquency of loan
    cout << "Expected value of a loan: " << expected << endl;

    //question 17
    vector<double> fifteen_delin;
    for (const Loan l : loans) {
        if (l.term == 15)
            fifteen_delin.push_back(l.d);
    }
    double fifteen_prob = 1 - mean(fifteen_delin); //probability that a single loan is not delinquent
    cout << "No delinquincy in next 25 15 year loans: " << pow(fifteen_prob, 25) << endl;

    cout << endl;

    /**PART 4 - Critical Thinking & Risk Analysis**/

    //question 20
    const int lb[4] = { 300, 620, 690, 720 }; //lower bounds for credit scores
    const int ub[4] = { 619, 689, 719, 850 }; //upper bounds for credit scores
    vector<vector<Loan> > loans_by_credit(4); //store four arrays of loans, based on credit score
    for (const Loan l : loans) {
        if (l.score >= lb[3]) //split loans based on credit score
            loans_by_credit[3].push_back(l);
        else if (l.score >= lb[2])
            loans_by_credit[2].push_back(l);
        else if (l.score >= lb[1])
            loans_by_credit[1].push_back(l);
        else
            loans_by_credit[0].push_back(l);
    }
    for (int i = 0; i < 4; i++) { //loop through each range
        cout << "Range: " << lb[i] << " - " << ub[i] << endl;
        vector<double> loan_price_ratio;
        int num_delinquent = 0;
        for (const Loan& l : loans_by_credit[i]) {
            loan_price_ratio.push_back(l.amt / l.price);
            num_delinquent += l.d;
        }
        cout << "Mean loan/pp ratio: " << mean(loan_price_ratio) << endl;
        cout << "Deviation loan/pp ratio: " << deviation(loan_price_ratio) << endl;
        cout << "# Delinquent: " << num_delinquent << endl;
        cout << "% Delinquent: " << 100 * (num_delinquent / ((double) loans_by_credit[i].size())) << endl;
    }

    cout << endl;

    //question 21
    vector<vector<Loan> > loans_by_term(2); //store 2 arrays of loans, based on term length
    for (const Loan l : loans) {
        if (l.term == 15) //split loans based on term length
            loans_by_term[0].push_back(l);
        else
            loans_by_term[1].push_back(l);
    }
    for (int i = 0; i < 2; i++) { //loop through both arrays
        cout << "Term: " << (i ? 30 : 15) << endl;
        vector<double> loan_price_ratio;
        int num_delinquent = 0;
        for (const Loan& l : loans_by_term[i]) {
            loan_price_ratio.push_back(l.amt / l.price);
            num_delinquent += l.d;
        }
        cout << "Mean loan/pp ratio: " << mean(loan_price_ratio) << endl;
        cout << "Deviation loan/pp ratio: " << deviation(loan_price_ratio) << endl;
        cout << "% Delinquent: " << 100 * (num_delinquent / ((double)loans_by_term[i].size())) << endl;
    }

    //question 22
    //note: in the final submission, "winter" is taken to consist of :
    // - New years (1/1/2010) to spring equinox (3/20/2010)
    // - Winter solstice (12/21/2010) to end of year (12/31/2010)
    //the calculation for only the first part is also included here
    vector<double> before_march;
    vector<double> after_march;
    vector<double> all_winter;
    vector<double> not_winter;
    for (const Loan& l : loans) {
        if (l.month < 3 || (l.month == 3 && l.day < 20)) { //split loans based on date
            before_march.push_back(l.d);
            all_winter.push_back(l.d);
        }
        else {
            after_march.push_back(l.d);
            if (l.month == 12 && l.day > 21) {
                all_winter.push_back(l.d);
            }
            else {
                not_winter.push_back(l.d);
            }
        }
    }
    cout << "1/1 - 3/19 delinquency rate: " << mean(before_march) << endl;
    cout << "3/20 - 12/31 delinquency rate: " << mean(after_march) << endl;
    cout << "1/1 - 3/19 + 12/22 - 12/31 delinquency rate: " << mean(all_winter) << endl;
    cout << "3/20 - 12/21 delinquency rate: " << mean(not_winter) << endl;

    return 0;
}
