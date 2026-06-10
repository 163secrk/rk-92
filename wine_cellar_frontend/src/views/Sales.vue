<template>
  <div class="sales-page">
    <div class="page-header">
      <div class="header-title">
        <h2>名酒销售管理</h2>
        <p>管理客户档案、销售订单和拍卖记录</p>
      </div>
      <el-tabs v-model="activeTab" class="header-tabs" @tab-change="handleTabChange">
        <el-tab-pane label="客户档案" name="customers" />
        <el-tab-pane label="售出订单" name="orders" />
        <el-tab-pane label="拍卖记录" name="auctions" />
      </el-tabs>
    </div>

    <div class="page-content">
      <div v-show="activeTab === 'customers'" class="tab-content">
        <div class="toolbar">
          <el-input
            v-model="customerSearch"
            placeholder="搜索客户姓名或电话"
            style="width: 240px"
            clearable
            @clear="loadCustomers"
            @keyup.enter="searchCustomers"
          >
            <template #prefix>
              <el-icon><Search /></el-icon>
            </template>
          </el-input>
          <el-select v-model="customerLevel" placeholder="会员等级" style="width: 140px" clearable @change="loadCustomers">
            <el-option label="普通客户" value="normal" />
            <el-option label="银卡会员" value="silver" />
            <el-option label="金卡会员" value="gold" />
            <el-option label="白金会员" value="platinum" />
            <el-option label="钻石会员" value="diamond" />
          </el-select>
          <el-button type="primary" @click="openCustomerForm()">
            <el-icon><Plus /></el-icon>
            新增客户
          </el-button>
        </div>

        <el-table :data="customers" stripe v-loading="customerLoading">
          <el-table-column prop="name" label="客户姓名" width="120" />
          <el-table-column prop="phone" label="联系电话" width="140" />
          <el-table-column prop="email" label="电子邮箱" width="180" show-overflow-tooltip />
          <el-table-column label="会员等级" width="120">
            <template #default="{ row }">
              <el-tag :type="getLevelTagType(row.level)">
                {{ row.level_display }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="total_orders" label="订单数" width="80" align="center" />
          <el-table-column label="累计消费" width="140" align="right">
            <template #default="{ row }">
              ¥{{ formatMoney(row.total_purchases) }}
            </template>
          </el-table-column>
          <el-table-column prop="created_at" label="创建时间" width="180">
            <template #default="{ row }">
              {{ formatDate(row.created_at) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="180" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link size="small" @click="openCustomerForm(row)">编辑</el-button>
              <el-button type="primary" link size="small" @click="viewCustomerOrders(row)">订单</el-button>
              <el-button type="danger" link size="small" @click="deleteCustomer(row)">删除</el-button>
            </template>
          </el-table-column>
        </el-table>

        <el-pagination
          v-model:current-page="customerPage"
          v-model:page-size="pageSize"
          :total="customerTotal"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          class="pagination"
          @size-change="loadCustomers"
          @current-change="loadCustomers"
        />
      </div>

      <div v-show="activeTab === 'orders'" class="tab-content">
        <div class="toolbar">
          <el-select v-model="orderStatus" placeholder="订单状态" style="width: 140px" clearable @change="loadOrders">
            <el-option label="草稿" value="draft" />
            <el-option label="已确认" value="confirmed" />
            <el-option label="已发货" value="shipped" />
            <el-option label="已完成" value="completed" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
          <el-button type="primary" @click="openOrderForm()">
            <el-icon><Plus /></el-icon>
            新建订单
          </el-button>
        </div>

        <el-table :data="orders" stripe v-loading="orderLoading">
          <el-table-column prop="order_no" label="订单编号" width="180" />
          <el-table-column prop="customer_name" label="客户" width="120" />
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="getOrderStatusType(row.status)">
                {{ row.status_display }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column label="订单金额" width="140" align="right">
            <template #default="{ row }">
              ¥{{ formatMoney(row.total_amount) }}
            </template>
          </el-table-column>
          <el-table-column prop="order_date" label="下单时间" width="180">
            <template #default="{ row }">
              {{ formatDate(row.order_date) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="280" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link size="small" @click="viewOrderDetail(row)">详情</el-button>
              <el-button type="success" link size="small" v-if="row.status === 'draft'" @click="confirmOrder(row)">确认</el-button>
              <el-button type="warning" link size="small" v-if="row.status === 'confirmed'" @click="shipOrder(row)">发货</el-button>
              <el-button type="success" link size="small" v-if="row.status === 'shipped'" @click="completeOrder(row)">完成</el-button>
              <el-button type="danger" link size="small" v-if="row.status === 'draft' || row.status === 'confirmed'" @click="cancelOrder(row)">取消</el-button>
            </template>
          </el-table-column>
        </el-table>

        <el-pagination
          v-model:current-page="orderPage"
          v-model:page-size="pageSize"
          :total="orderTotal"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          class="pagination"
          @size-change="loadOrders"
          @current-change="loadOrders"
        />
      </div>

      <div v-show="activeTab === 'auctions'" class="tab-content">
        <div class="toolbar">
          <el-select v-model="auctionStatus" placeholder="拍卖状态" style="width: 140px" clearable @change="loadAuctions">
            <el-option label="即将开拍" value="upcoming" />
            <el-option label="拍卖中" value="ongoing" />
            <el-option label="已结束" value="ended" />
            <el-option label="已取消" value="cancelled" />
          </el-select>
          <el-button type="primary" @click="openAuctionForm()">
            <el-icon><Plus /></el-icon>
            创建拍卖
          </el-button>
        </div>

        <el-table :data="auctions" stripe v-loading="auctionLoading">
          <el-table-column prop="title" label="拍卖标题" min-width="200" show-overflow-tooltip />
          <el-table-column prop="wine_name" label="酒品" width="180" />
          <el-table-column prop="wine_vintage" label="年份" width="80" align="center" />
          <el-table-column prop="quantity" label="数量(瓶)" width="100" align="center" />
          <el-table-column label="起拍价" width="120" align="right">
            <template #default="{ row }">
              ¥{{ formatMoney(row.start_price) }}
            </template>
          </el-table-column>
          <el-table-column label="当前出价" width="120" align="right">
            <template #default="{ row }">
              <span v-if="row.current_bid">¥{{ formatMoney(row.current_bid) }}</span>
              <span v-else class="muted">暂无出价</span>
            </template>
          </el-table-column>
          <el-table-column label="状态" width="100">
            <template #default="{ row }">
              <el-tag :type="getAuctionStatusType(row.status)">
                {{ row.status_display }}
              </el-tag>
            </template>
          </el-table-column>
          <el-table-column prop="bid_count" label="出价次数" width="100" align="center" />
          <el-table-column label="开始时间" width="180">
            <template #default="{ row }">
              {{ formatDate(row.start_time) }}
            </template>
          </el-table-column>
          <el-table-column label="操作" width="240" fixed="right">
            <template #default="{ row }">
              <el-button type="primary" link size="small" @click="viewAuctionDetail(row)">详情</el-button>
              <el-button type="success" link size="small" v-if="row.status === 'upcoming'" @click="startAuction(row)">开始</el-button>
              <el-button type="warning" link size="small" v-if="row.status === 'ongoing'" @click="openBidForm(row)">出价</el-button>
              <el-button type="danger" link size="small" v-if="row.status === 'ongoing'" @click="endAuction(row)">结束</el-button>
            </template>
          </el-table-column>
        </el-table>

        <el-pagination
          v-model:current-page="auctionPage"
          v-model:page-size="pageSize"
          :total="auctionTotal"
          :page-sizes="[10, 20, 50, 100]"
          layout="total, sizes, prev, pager, next, jumper"
          class="pagination"
          @size-change="loadAuctions"
          @current-change="loadAuctions"
        />
      </div>
    </div>

    <el-dialog v-model="customerFormVisible" :title="editingCustomer ? '编辑客户' : '新增客户'" width="600px">
      <el-form :model="customerForm" label-width="100px">
        <el-form-item label="客户姓名">
          <el-input v-model="customerForm.name" />
        </el-form-item>
        <el-form-item label="性别">
          <el-radio-group v-model="customerForm.gender">
            <el-radio value="male">男</el-radio>
            <el-radio value="female">女</el-radio>
            <el-radio value="other">其他</el-radio>
          </el-radio-group>
        </el-form-item>
        <el-form-item label="联系电话">
          <el-input v-model="customerForm.phone" />
        </el-form-item>
        <el-form-item label="电子邮箱">
          <el-input v-model="customerForm.email" />
        </el-form-item>
        <el-form-item label="身份证号">
          <el-input v-model="customerForm.id_card" />
        </el-form-item>
        <el-form-item label="联系地址">
          <el-input v-model="customerForm.address" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="customerForm.notes" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="customerFormVisible = false">取消</el-button>
        <el-button type="primary" @click="saveCustomer">保存</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="orderFormVisible" title="新建订单" width="800px">
      <el-form :model="orderForm" label-width="100px">
        <el-form-item label="选择客户">
          <el-select
            v-model="orderForm.customer"
            placeholder="搜索并选择客户"
            filterable
            remote
            reserve-keyword
            :remote-method="remoteSearchCustomer"
            style="width: 100%"
          >
            <el-option
              v-for="cust in customerOptions"
              :key="cust.id"
              :label="`${cust.name} - ${cust.phone}`"
              :value="cust.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="支付方式">
          <el-select v-model="orderForm.payment_method" placeholder="请选择">
            <el-option label="银行转账" value="bank_transfer" />
            <el-option label="支付宝" value="alipay" />
            <el-option label="微信支付" value="wechat" />
            <el-option label="现金" value="cash" />
            <el-option label="信用卡" value="credit_card" />
            <el-option label="其他" value="other" />
          </el-select>
        </el-form-item>
        <el-form-item label="收货地址">
          <el-input v-model="orderForm.shipping_address" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="折扣金额">
          <el-input-number v-model="orderForm.discount" :min="0" :precision="2" />
        </el-form-item>
        <el-form-item label="运费">
          <el-input-number v-model="orderForm.shipping_fee" :min="0" :precision="2" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="orderForm.notes" type="textarea" :rows="2" />
        </el-form-item>
        <el-form-item label="订单商品">
          <div class="order-items">
            <el-table :data="orderForm.items" size="small" border>
              <el-table-column label="酒品" min-width="200">
                <template #default="{ row, $index }">
                  <el-select
                    v-model="row.wine"
                    placeholder="选择酒品"
                    filterable
                    style="width: 100%"
                    @change="onWineSelect(row, $index)"
                  >
                    <el-option
                      v-for="wine in wineOptions"
                      :key="wine.id"
                      :label="`${wine.name} ${wine.vintage} (库存:${wine.quantity}瓶)`"
                      :value="wine.id"
                    />
                  </el-select>
                </template>
              </el-table-column>
              <el-table-column label="单价(元)" width="120">
                <template #default="{ row }">
                  <el-input-number v-model="row.unit_price" :min="0" :precision="2" size="small" style="width: 100%" />
                </template>
              </el-table-column>
              <el-table-column label="数量(瓶)" width="100">
                <template #default="{ row }">
                  <el-input-number v-model="row.quantity" :min="1" size="small" style="width: 100%" />
                </template>
              </el-table-column>
              <el-table-column label="小计(元)" width="120" align="right">
                <template #default="{ row }">
                  ¥{{ formatMoney(row.unit_price * row.quantity) }}
                </template>
              </el-table-column>
              <el-table-column label="操作" width="60">
                <template #default="{ $index }">
                  <el-button type="danger" link size="small" @click="removeOrderItem($index)">删除</el-button>
                </template>
              </el-table-column>
            </el-table>
            <el-button type="primary" size="small" style="margin-top: 8px" @click="addOrderItem">
              <el-icon><Plus /></el-icon>
              添加商品
            </el-button>
          </div>
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="orderFormVisible = false">取消</el-button>
        <el-button type="primary" @click="createOrder">创建订单</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="auctionFormVisible" title="创建拍卖" width="600px">
      <el-form :model="auctionForm" label-width="100px">
        <el-form-item label="拍卖标题">
          <el-input v-model="auctionForm.title" />
        </el-form-item>
        <el-form-item label="选择酒品">
          <el-select v-model="auctionForm.wine" placeholder="选择酒品" filterable style="width: 100%">
            <el-option
              v-for="wine in wineOptions"
              :key="wine.id"
              :label="`${wine.name} ${wine.vintage} (库存:${wine.quantity}瓶)`"
              :value="wine.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="拍卖数量">
          <el-input-number v-model="auctionForm.quantity" :min="1" />
        </el-form-item>
        <el-form-item label="起拍价(元)">
          <el-input-number v-model="auctionForm.start_price" :min="0" :precision="2" />
        </el-form-item>
        <el-form-item label="保留价(元)">
          <el-input-number v-model="auctionForm.reserve_price" :min="0" :precision="2" />
        </el-form-item>
        <el-form-item label="开始时间">
          <el-date-picker
            v-model="auctionForm.start_time"
            type="datetime"
            placeholder="选择开始时间"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="结束时间">
          <el-date-picker
            v-model="auctionForm.end_time"
            type="datetime"
            placeholder="选择结束时间"
            style="width: 100%"
          />
        </el-form-item>
        <el-form-item label="拍卖行">
          <el-input v-model="auctionForm.auction_house" />
        </el-form-item>
        <el-form-item label="拍品编号">
          <el-input v-model="auctionForm.lot_number" />
        </el-form-item>
        <el-form-item label="备注">
          <el-input v-model="auctionForm.notes" type="textarea" :rows="3" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="auctionFormVisible = false">取消</el-button>
        <el-button type="primary" @click="createAuction">创建</el-button>
      </template>
    </el-dialog>

    <el-dialog v-model="bidFormVisible" title="出价" width="500px">
      <el-form :model="bidForm" label-width="100px">
        <el-form-item label="选择客户">
          <el-select
            v-model="bidForm.customer"
            placeholder="搜索并选择客户"
            filterable
            remote
            reserve-keyword
            :remote-method="remoteSearchCustomer"
            style="width: 100%"
          >
            <el-option
              v-for="cust in customerOptions"
              :key="cust.id"
              :label="`${cust.name} - ${cust.phone}`"
              :value="cust.id"
            />
          </el-select>
        </el-form-item>
        <el-form-item label="出价金额(元)">
          <el-input-number v-model="bidForm.amount" :min="0" :precision="2" style="width: 100%" />
        </el-form-item>
      </el-form>
      <template #footer>
        <el-button @click="bidFormVisible = false">取消</el-button>
        <el-button type="primary" @click="submitBid">确认出价</el-button>
      </template>
    </el-dialog>

    <el-drawer v-model="orderDetailVisible" title="订单详情" size="600px">
      <div v-if="currentOrder" class="order-detail">
        <div class="detail-section">
          <h3>订单信息</h3>
          <div class="detail-grid">
            <div class="detail-item">
              <span class="label">订单编号：</span>
              <span class="value">{{ currentOrder.order_no }}</span>
            </div>
            <div class="detail-item">
              <span class="label">订单状态：</span>
              <el-tag :type="getOrderStatusType(currentOrder.status)">
                {{ currentOrder.status_display }}
              </el-tag>
            </div>
            <div class="detail-item">
              <span class="label">客户：</span>
              <span class="value">{{ currentOrder.customer_name }}</span>
            </div>
            <div class="detail-item">
              <span class="label">支付方式：</span>
              <span class="value">{{ currentOrder.payment_method_display || '-' }}</span>
            </div>
            <div class="detail-item">
              <span class="label">下单时间：</span>
              <span class="value">{{ formatDate(currentOrder.order_date) }}</span>
            </div>
            <div class="detail-item">
              <span class="label">收货地址：</span>
              <span class="value">{{ currentOrder.shipping_address || '-' }}</span>
            </div>
          </div>
        </div>

        <div class="detail-section">
          <h3>商品明细</h3>
          <el-table :data="currentOrder.items" size="small" border>
            <el-table-column prop="wine_name" label="酒品" />
            <el-table-column prop="wine_vintage" label="年份" width="80" align="center" />
            <el-table-column label="单价" width="100" align="right">
              <template #default="{ row }">
                ¥{{ formatMoney(row.unit_price) }}
              </template>
            </el-table-column>
            <el-table-column prop="quantity" label="数量" width="80" align="center" />
            <el-table-column label="小计" width="120" align="right">
              <template #default="{ row }">
                ¥{{ formatMoney(row.total_price) }}
              </template>
            </el-table-column>
          </el-table>
        </div>

        <div class="detail-section">
          <h3>金额明细</h3>
          <div class="amount-summary">
            <div class="amount-item">
              <span>商品小计：</span>
              <span>¥{{ formatMoney(currentOrder.subtotal) }}</span>
            </div>
            <div class="amount-item">
              <span>折扣：</span>
              <span>-¥{{ formatMoney(currentOrder.discount) }}</span>
            </div>
            <div class="amount-item">
              <span>运费：</span>
              <span>¥{{ formatMoney(currentOrder.shipping_fee) }}</span>
            </div>
            <div class="amount-item total">
              <span>订单总额：</span>
              <span>¥{{ formatMoney(currentOrder.total_amount) }}</span>
            </div>
          </div>
        </div>

        <div v-if="currentOrder.notes" class="detail-section">
          <h3>备注</h3>
          <p>{{ currentOrder.notes }}</p>
        </div>
      </div>
    </el-drawer>

    <el-drawer v-model="auctionDetailVisible" title="拍卖详情" size="600px">
      <div v-if="currentAuction" class="auction-detail">
        <div class="detail-section">
          <h3>拍卖信息</h3>
          <div class="detail-grid">
            <div class="detail-item">
              <span class="label">拍卖标题：</span>
              <span class="value">{{ currentAuction.title }}</span>
            </div>
            <div class="detail-item">
              <span class="label">状态：</span>
              <el-tag :type="getAuctionStatusType(currentAuction.status)">
                {{ currentAuction.status_display }}
              </el-tag>
            </div>
            <div class="detail-item">
              <span class="label">酒品：</span>
              <span class="value">{{ currentAuction.wine_name }} {{ currentAuction.wine_vintage }}</span>
            </div>
            <div class="detail-item">
              <span class="label">数量：</span>
              <span class="value">{{ currentAuction.quantity }} 瓶</span>
            </div>
            <div class="detail-item">
              <span class="label">起拍价：</span>
              <span class="value">¥{{ formatMoney(currentAuction.start_price) }}</span>
            </div>
            <div class="detail-item">
              <span class="label">保留价：</span>
              <span class="value">¥{{ formatMoney(currentAuction.reserve_price) }}</span>
            </div>
            <div class="detail-item">
              <span class="label">当前出价：</span>
              <span class="value highlight">
                {{ currentAuction.current_bid ? '¥' + formatMoney(currentAuction.current_bid) : '暂无出价' }}
              </span>
            </div>
            <div class="detail-item">
              <span class="label">成交价：</span>
              <span class="value">{{ currentAuction.final_price ? '¥' + formatMoney(currentAuction.final_price) : '-' }}</span>
            </div>
            <div class="detail-item">
              <span class="label">开始时间：</span>
              <span class="value">{{ formatDate(currentAuction.start_time) }}</span>
            </div>
            <div class="detail-item">
              <span class="label">结束时间：</span>
              <span class="value">{{ formatDate(currentAuction.end_time) }}</span>
            </div>
            <div class="detail-item">
              <span class="label">出价次数：</span>
              <span class="value">{{ currentAuction.bid_count }} 次</span>
            </div>
            <div class="detail-item">
              <span class="label">中标客户：</span>
              <span class="value">{{ currentAuction.winner_name || '-' }}</span>
            </div>
          </div>
        </div>

        <div v-if="currentAuction.bids && currentAuction.bids.length > 0" class="detail-section">
          <h3>出价记录</h3>
          <el-table :data="currentAuction.bids" size="small" border>
            <el-table-column prop="bidder_name" label="出价人" />
            <el-table-column label="出价金额" align="right">
              <template #default="{ row }">
                ¥{{ formatMoney(row.amount) }}
              </template>
            </el-table-column>
            <el-table-column prop="bid_time" label="出价时间" width="180">
              <template #default="{ row }">
                {{ formatDate(row.bid_time) }}
              </template>
            </el-table-column>
          </el-table>
        </div>

        <div v-if="currentAuction.notes" class="detail-section">
          <h3>备注</h3>
          <p>{{ currentAuction.notes }}</p>
        </div>
      </div>
    </el-drawer>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue'
import { ElMessage, ElMessageBox } from 'element-plus'
import { Search, Plus } from '@element-plus/icons-vue'
import {
  getCustomers, getCustomer, createCustomer, updateCustomer,
  deleteCustomer as deleteCustomerApi, searchCustomers as searchCustomersApi,
  getOrders, getOrder, createOrder as createOrderApi, confirmOrder as confirmOrderApi,
  cancelOrder as cancelOrderApi, shipOrder as shipOrderApi, completeOrder as completeOrderApi,
  getAuctions, getAuction, createAuction as createAuctionApi, startAuction as startAuctionApi,
  endAuction as endAuctionApi, placeBid, getBidHistory
} from '@/api/sales'
import { getWines } from '@/api/collection'

const activeTab = ref('customers')

const customers = ref([])
const customerLoading = ref(false)
const customerPage = ref(1)
const customerTotal = ref(0)
const customerSearch = ref('')
const customerLevel = ref('')

const orders = ref([])
const orderLoading = ref(false)
const orderPage = ref(1)
const orderTotal = ref(0)
const orderStatus = ref('')

const auctions = ref([])
const auctionLoading = ref(false)
const auctionPage = ref(1)
const auctionTotal = ref(0)
const auctionStatus = ref('')

const pageSize = ref(20)

const customerFormVisible = ref(false)
const editingCustomer = ref(null)
const customerForm = ref({
  name: '',
  gender: '',
  phone: '',
  email: '',
  id_card: '',
  address: '',
  notes: ''
})

const orderFormVisible = ref(false)
const orderForm = ref({
  customer: null,
  payment_method: '',
  shipping_address: '',
  discount: 0,
  shipping_fee: 0,
  notes: '',
  items: []
})
const customerOptions = ref([])
const wineOptions = ref([])

const auctionFormVisible = ref(false)
const auctionForm = ref({
  title: '',
  wine: null,
  quantity: 1,
  start_price: 0,
  reserve_price: 0,
  start_time: '',
  end_time: '',
  auction_house: '',
  lot_number: '',
  notes: ''
})

const bidFormVisible = ref(false)
const bidForm = ref({
  customer: null,
  amount: 0
})
const currentAuction = ref(null)

const orderDetailVisible = ref(false)
const currentOrder = ref(null)

const auctionDetailVisible = ref(false)

function handleTabChange(tab) {
  if (tab === 'customers') {
    loadCustomers()
  } else if (tab === 'orders') {
    loadOrders()
  } else if (tab === 'auctions') {
    loadAuctions()
  }
}

async function loadCustomers() {
  customerLoading.value = true
  try {
    const params = {
      page: customerPage.value,
      page_size: pageSize.value
    }
    if (customerLevel.value) params.level = customerLevel.value
    const res = await getCustomers(params)
    customers.value = res.results
    customerTotal.value = res.count
  } catch (e) {
    console.error(e)
  } finally {
    customerLoading.value = false
  }
}

async function searchCustomers() {
  customerPage.value = 1
  customerLoading.value = true
  try {
    const params = {
      page: 1,
      page_size: pageSize.value,
      q: customerSearch.value
    }
    const res = await getCustomers(params)
    customers.value = res.results
    customerTotal.value = res.count
  } catch (e) {
    console.error(e)
  } finally {
    customerLoading.value = false
  }
}

function openCustomerForm(customer = null) {
  editingCustomer.value = customer
  if (customer) {
    customerForm.value = { ...customer }
  } else {
    customerForm.value = {
      name: '',
      gender: '',
      phone: '',
      email: '',
      id_card: '',
      address: '',
      notes: ''
    }
  }
  customerFormVisible.value = true
}

async function saveCustomer() {
  try {
    if (editingCustomer.value) {
      await updateCustomer(editingCustomer.value.id, customerForm.value)
      ElMessage.success('更新成功')
    } else {
      await createCustomer(customerForm.value)
      ElMessage.success('创建成功')
    }
    customerFormVisible.value = false
    loadCustomers()
  } catch (e) {
    console.error(e)
    ElMessage.error('保存失败')
  }
}

async function deleteCustomer(customer) {
  try {
    await ElMessageBox.confirm(`确定要删除客户 "${customer.name}" 吗？`, '提示', {
      type: 'warning'
    })
    await deleteCustomerApi(customer.id)
    ElMessage.success('删除成功')
    loadCustomers()
  } catch (e) {
    if (e !== 'cancel') {
      console.error(e)
    }
  }
}

function viewCustomerOrders(customer) {
  activeTab.value = 'orders'
  orderStatus.value = ''
  loadOrders()
}

async function loadOrders() {
  orderLoading.value = true
  try {
    const params = {
      page: orderPage.value,
      page_size: pageSize.value
    }
    if (orderStatus.value) params.status = orderStatus.value
    const res = await getOrders(params)
    orders.value = res.results
    orderTotal.value = res.count
  } catch (e) {
    console.error(e)
  } finally {
    orderLoading.value = false
  }
}

async function viewOrderDetail(order) {
  try {
    const res = await getOrder(order.id)
    currentOrder.value = res
    orderDetailVisible.value = true
  } catch (e) {
    console.error(e)
  }
}

async function openOrderForm() {
  orderForm.value = {
    customer: null,
    payment_method: '',
    shipping_address: '',
    discount: 0,
    shipping_fee: 0,
    notes: '',
    items: [{ wine: null, unit_price: 0, quantity: 1, notes: '' }]
  }
  await loadWineOptions()
  orderFormVisible.value = true
}

async function loadWineOptions() {
  try {
    const res = await getWines({ status: 'cellared', page_size: 100 })
    wineOptions.value = res.results
  } catch (e) {
    console.error(e)
  }
}

async function remoteSearchCustomer(keyword) {
  if (keyword) {
    try {
      const res = await searchCustomersApi(keyword)
      customerOptions.value = res
    } catch (e) {
      console.error(e)
    }
  } else {
    customerOptions.value = []
  }
}

function addOrderItem() {
  orderForm.value.items.push({ wine: null, unit_price: 0, quantity: 1, notes: '' })
}

function removeOrderItem(index) {
  orderForm.value.items.splice(index, 1)
}

function onWineSelect(row, index) {
  const wine = wineOptions.value.find(w => w.id === row.wine)
  if (wine) {
    row.unit_price = wine.current_value
  }
}

async function createOrder() {
  if (!orderForm.value.customer) {
    ElMessage.warning('请选择客户')
    return
  }
  if (orderForm.value.items.length === 0) {
    ElMessage.warning('请添加商品')
    return
  }
  const invalidItems = orderForm.value.items.filter(item => !item.wine || item.quantity <= 0 || item.unit_price <= 0)
  if (invalidItems.length > 0) {
    ElMessage.warning('请完善所有商品信息')
    return
  }
  try {
    await createOrderApi(orderForm.value)
    ElMessage.success('订单创建成功')
    orderFormVisible.value = false
    loadOrders()
  } catch (e) {
    console.error(e)
    ElMessage.error('创建失败')
  }
}

async function confirmOrder(order) {
  try {
    await ElMessageBox.confirm(`确定要确认订单 "${order.order_no}" 吗？确认后将扣减库存。`, '提示', {
      type: 'warning'
    })
    await confirmOrderApi(order.id)
    ElMessage.success('订单已确认，库存已扣减')
    loadOrders()
  } catch (e) {
    if (e !== 'cancel') {
      console.error(e)
      ElMessage.error(e.response?.data?.error || '确认失败')
    }
  }
}

async function cancelOrder(order) {
  try {
    await ElMessageBox.confirm(`确定要取消订单 "${order.order_no}" 吗？取消后将恢复库存。`, '提示', {
      type: 'warning'
    })
    await cancelOrderApi(order.id)
    ElMessage.success('订单已取消，库存已恢复')
    loadOrders()
  } catch (e) {
    if (e !== 'cancel') {
      console.error(e)
      ElMessage.error(e.response?.data?.error || '取消失败')
    }
  }
}

async function shipOrder(order) {
  try {
    const { value } = await ElMessageBox.prompt('请输入物流单号', '发货', {
      confirmButtonText: '确认发货',
      cancelButtonText: '取消',
      inputPlaceholder: '请输入物流单号（可选）'
    })
    await shipOrderApi(order.id, { tracking_number: value || '' })
    ElMessage.success('已发货')
    loadOrders()
  } catch (e) {
    if (e !== 'cancel') {
      console.error(e)
    }
  }
}

async function completeOrder(order) {
  try {
    await ElMessageBox.confirm(`确定要完成订单 "${order.order_no}" 吗？`, '提示', {
      type: 'warning'
    })
    await completeOrderApi(order.id)
    ElMessage.success('订单已完成')
    loadOrders()
  } catch (e) {
    if (e !== 'cancel') {
      console.error(e)
    }
  }
}

async function loadAuctions() {
  auctionLoading.value = true
  try {
    const params = {
      page: auctionPage.value,
      page_size: pageSize.value
    }
    if (auctionStatus.value) params.status = auctionStatus.value
    const res = await getAuctions(params)
    auctions.value = res.results
    auctionTotal.value = res.count
  } catch (e) {
    console.error(e)
  } finally {
    auctionLoading.value = false
  }
}

async function viewAuctionDetail(auction) {
  try {
    const [auctionRes, bidRes] = await Promise.all([
      getAuction(auction.id),
      getBidHistory(auction.id)
    ])
    currentAuction.value = { ...auctionRes, bids: bidRes }
    auctionDetailVisible.value = true
  } catch (e) {
    console.error(e)
  }
}

async function openAuctionForm() {
  auctionForm.value = {
    title: '',
    wine: null,
    quantity: 1,
    start_price: 0,
    reserve_price: 0,
    start_time: '',
    end_time: '',
    auction_house: '',
    lot_number: '',
    notes: ''
  }
  await loadWineOptions()
  auctionFormVisible.value = true
}

async function createAuction() {
  if (!auctionForm.value.title || !auctionForm.value.wine || !auctionForm.value.start_time || !auctionForm.value.end_time) {
    ElMessage.warning('请填写必填信息')
    return
  }
  try {
    await createAuctionApi(auctionForm.value)
    ElMessage.success('拍卖创建成功')
    auctionFormVisible.value = false
    loadAuctions()
  } catch (e) {
    console.error(e)
    ElMessage.error('创建失败')
  }
}

async function startAuction(auction) {
  try {
    await ElMessageBox.confirm(`确定要开始拍卖 "${auction.title}" 吗？`, '提示', {
      type: 'warning'
    })
    await startAuctionApi(auction.id)
    ElMessage.success('拍卖已开始')
    loadAuctions()
  } catch (e) {
    if (e !== 'cancel') {
      console.error(e)
    }
  }
}

async function endAuction(auction) {
  try {
    await ElMessageBox.confirm(`确定要结束拍卖 "${auction.title}" 吗？结束后将根据出价情况扣减库存。`, '提示', {
      type: 'warning'
    })
    await endAuctionApi(auction.id)
    ElMessage.success('拍卖已结束')
    loadAuctions()
  } catch (e) {
    if (e !== 'cancel') {
      console.error(e)
      ElMessage.error(e.response?.data?.error || '操作失败')
    }
  }
}

function openBidForm(auction) {
  currentAuction.value = auction
  bidForm.value = {
    customer: null,
    amount: auction.current_bid ? auction.current_bid * 1.1 : auction.start_price
  }
  bidFormVisible.value = true
}

async function submitBid() {
  if (!bidForm.value.customer) {
    ElMessage.warning('请选择客户')
    return
  }
  if (!bidForm.value.amount || bidForm.value.amount <= 0) {
    ElMessage.warning('请输入有效出价金额')
    return
  }
  try {
    await placeBid(currentAuction.value.id, bidForm.value)
    ElMessage.success('出价成功')
    bidFormVisible.value = false
    loadAuctions()
  } catch (e) {
    console.error(e)
    ElMessage.error(e.response?.data?.error || '出价失败')
  }
}

function getLevelTagType(level) {
  const map = {
    normal: 'info',
    silver: 'info',
    gold: 'warning',
    platinum: 'success',
    diamond: 'danger'
  }
  return map[level] || 'info'
}

function getOrderStatusType(status) {
  const map = {
    draft: 'info',
    confirmed: 'primary',
    shipped: 'warning',
    completed: 'success',
    cancelled: 'danger',
    returned: 'info'
  }
  return map[status] || 'info'
}

function getAuctionStatusType(status) {
  const map = {
    upcoming: 'info',
    ongoing: 'primary',
    ended: 'success',
    cancelled: 'danger'
  }
  return map[status] || 'info'
}

function formatMoney(value) {
  if (value === null || value === undefined) return '0.00'
  return Number(value).toLocaleString('zh-CN', { minimumFractionDigits: 2, maximumFractionDigits: 2 })
}

function formatDate(value) {
  if (!value) return '-'
  return new Date(value).toLocaleString('zh-CN')
}

onMounted(() => {
  loadCustomers()
})
</script>

<style scoped>
.sales-page {
  padding: 24px;
}

.page-header {
  background: white;
  border-radius: 12px;
  padding: 24px;
  margin-bottom: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.header-title h2 {
  margin: 0 0 4px 0;
  font-size: 22px;
  color: #1e293b;
}

.header-title p {
  margin: 0;
  color: #64748b;
  font-size: 14px;
}

.header-tabs {
  margin-top: 16px;
}

.page-content {
  background: white;
  border-radius: 12px;
  padding: 20px;
  box-shadow: 0 2px 8px rgba(0, 0, 0, 0.06);
}

.tab-content {
  min-height: 400px;
}

.toolbar {
  display: flex;
  gap: 12px;
  margin-bottom: 16px;
  flex-wrap: wrap;
}

.pagination {
  margin-top: 20px;
  justify-content: flex-end;
  display: flex;
}

.muted {
  color: #94a3b8;
}

.order-items {
  width: 100%;
}

.detail-section {
  margin-bottom: 24px;
}

.detail-section h3 {
  margin: 0 0 12px 0;
  font-size: 16px;
  color: #1e293b;
  padding-bottom: 8px;
  border-bottom: 1px solid #e2e8f0;
}

.detail-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 12px;
}

.detail-item {
  display: flex;
  align-items: center;
  gap: 8px;
}

.detail-item .label {
  color: #64748b;
  font-size: 14px;
  white-space: nowrap;
}

.detail-item .value {
  color: #1e293b;
  font-weight: 500;
}

.detail-item .value.highlight {
  color: #ef4444;
  font-size: 18px;
  font-weight: 600;
}

.amount-summary {
  display: flex;
  flex-direction: column;
  gap: 8px;
  max-width: 300px;
  margin-left: auto;
}

.amount-item {
  display: flex;
  justify-content: space-between;
  color: #64748b;
}

.amount-item.total {
  font-size: 18px;
  font-weight: 600;
  color: #ef4444;
  padding-top: 8px;
  border-top: 1px solid #e2e8f0;
}
</style>
